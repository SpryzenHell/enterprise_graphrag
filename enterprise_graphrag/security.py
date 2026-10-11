from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Callable

import httpx


PATTERNS = [
    r"ignore\\s+(?:(?:all|any)\\s+)?(?:(?:previous|prior)\\s+)?instructions",
    r"system\\s+prompt",
    r"developer\\s+message",
    r"reveal\\s+(your|the)\\s+(prompt|instructions|secrets?)",
    r"send\\s+(this|the)\\s+(data|document|prompt)",
    r"disable\\s+(safety|security|policy)",
    r"execute\\s+.*(shell|command|code)",
    r"you\\s+are\\s+now\\s+(the|a)",
]


class SecurityGateway:
    """Tenant retrieval content gate using markers, optional vLLM PPL, and an optional semantic detector.

    When SECURITY_CLASSIFIER_MODEL is set, the classifier is loaded during construction.
    Explicitly enabling a classifier is fail-closed: model-load or inference errors block the
    inspected item instead of silently reverting to the weaker marker-only behavior.
    """

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "",
        threshold: float = 80.0,
        marker_threshold: int = 2,
        classifier_model: str = "",
        classifier_threshold: float = 0.5,
        classifier_max_length: int = 8192,
        classifier_device: str = "auto",
        classifier_score_fn: Callable[[str], float] | None = None,
    ) -> None:
        if marker_threshold < 1:
            raise ValueError("marker_threshold must be at least 1")
        if not 0.0 <= classifier_threshold <= 1.0:
            raise ValueError("classifier_threshold must be between 0 and 1")
        if classifier_max_length < 8 or classifier_max_length > 8192:
            raise ValueError("classifier_max_length must be between 8 and 8192")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.threshold = threshold
        self.marker_threshold = marker_threshold
        self.classifier_model = classifier_model.strip()
        self.classifier_threshold = float(classifier_threshold)
        self.classifier_max_length = int(classifier_max_length)
        self.patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in PATTERNS
        ]
        self._classifier_score_fn = classifier_score_fn
        self._classifier_enabled = bool(self.classifier_model or classifier_score_fn)
        self._classifier_tokenizer = None
        self._classifier = None
        self._classifier_torch = None
        self._classifier_device = None
        self._positive_class_index = 1

        if self.classifier_model:
            try:
                self._load_semantic_classifier(classifier_device)
            except Exception as exc:
                raise RuntimeError(
                    f"Semantic injection classifier {self.classifier_model!r} could not be loaded"
                ) from exc

    def _load_semantic_classifier(self, requested_device: str) -> None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        if requested_device == "auto":
            if torch.cuda.is_available():
                # Keep vLLM on GPU 0 when a second GPU is available.
                requested_device = "cuda:1" if torch.cuda.device_count() > 1 else "cuda:0"
            else:
                requested_device = "cpu"

        self._classifier_torch = torch
        self._classifier_device = torch.device(requested_device)
        self._classifier_tokenizer = AutoTokenizer.from_pretrained(self.classifier_model)
        self._classifier = AutoModelForSequenceClassification.from_pretrained(self.classifier_model)
        self._classifier.to(self._classifier_device)
        self._classifier.eval()

        labels = {
            int(index): str(label)
            for index, label in (self._classifier.config.id2label or {}).items()
        }
        candidates = [
            index for index, label in labels.items()
            if "inject" in label.lower() and "non" not in label.lower()
        ]
        if candidates:
            self._positive_class_index = candidates[0]
        elif int(self._classifier.config.num_labels) == 2:
            # Binary sequence-classification checkpoints conventionally map positive to index 1.
            self._positive_class_index = 1
        else:
            raise RuntimeError(f"Cannot identify injection class in classifier labels: {labels}")

    def _semantic_score(self, text: str) -> float:
        if self._classifier_score_fn is not None:
            score = float(self._classifier_score_fn(text))
        else:
            if not (
                self._classifier_enabled
                and self._classifier_tokenizer is not None
                and self._classifier is not None
                and self._classifier_torch is not None
            ):
                raise RuntimeError("semantic classifier was enabled but is not initialized")

            encoded = self._classifier_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.classifier_max_length,
            )
            encoded = {
                key: value.to(self._classifier_device)
                for key, value in encoded.items()
            }
            with self._classifier_torch.inference_mode():
                logits = self._classifier(**encoded).logits.float()
                score = float(
                    self._classifier_torch.softmax(logits, dim=-1)[0, self._positive_class_index].item()
                )

        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError("semantic classifier returned an invalid probability")
        return score

    def perplexity(self, text: str) -> float | None:
        if not (self.base_url and self.model):
            return None

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = httpx.post(
                f"{self.base_url}/v1/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "prompt": text[:12000],
                    "max_tokens": 1,
                    "temperature": 0.0,
                    "prompt_logprobs": 1,
                    "return_token_ids": True,
                },
                timeout=60,
            )
            response.raise_for_status()
            choice = response.json()["choices"][0]
            entries = choice.get("prompt_logprobs") or []
            token_ids = choice.get("prompt_token_ids") or []
            if len(entries) != len(token_ids):
                return None

            observed = []
            for position, entry in enumerate(entries):
                if position == 0 or entry is None:
                    continue
                token_id = token_ids[position]
                token_data = entry.get(str(token_id))
                if token_data is None:
                    token_data = entry.get(token_id)
                if not isinstance(token_data, dict):
                    continue
                logprob = token_data.get("logprob")
                if isinstance(logprob, (int, float)):
                    observed.append(float(logprob))

            if not observed:
                return None
            try:
                return float(math.exp(-(sum(observed) / len(observed))))
            except OverflowError:
                return None
        except (
            OSError,
            httpx.HTTPError,
            KeyError,
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _normalize(text: str) -> str:
        normalized = unicodedata.normalize("NFKC", text)
        return "".join(
            char
            for char in normalized
            if char not in "\\u200b\\u200c\\u200d\\ufeff"
        )

    @staticmethod
    def _decision(
        allowed: bool,
        reason: str,
        marker_count: int,
        perplexity: float | None = None,
        classifier_score: float | None = None,
    ) -> dict:
        return {
            "allowed": allowed,
            "reason": reason,
            "marker_count": marker_count,
            "perplexity": perplexity,
            "classifier_score": classifier_score,
        }

    def inspect(self, text: str, direct: bool = False) -> dict:
        text = self._normalize(text)
        marker_count = sum(
            len(pattern.findall(text))
            for pattern in self.patterns
        )

        if direct and marker_count:
            return self._decision(False, "direct injection marker", marker_count)
        if marker_count >= self.marker_threshold:
            return self._decision(False, "retrieved injection markers", marker_count)

        classifier_score = None
        if self._classifier_enabled:
            try:
                classifier_score = self._semantic_score(text)
            except Exception:
                # An explicitly configured detector must not silently fail open.
                return self._decision(
                    False,
                    "semantic injection classifier failure (blocked closed)",
                    marker_count,
                )
            if classifier_score >= self.classifier_threshold:
                return self._decision(
                    False,
                    "semantic injection classifier",
                    marker_count,
                    classifier_score=classifier_score,
                )

        perplexity = self.perplexity(text)
        if (
            perplexity is not None
            and perplexity >= self.threshold
            and marker_count >= 1
        ):
            return self._decision(
                False,
                "high perplexity plus injection marker",
                marker_count,
                perplexity,
                classifier_score,
            )

        return self._decision(
            True,
            "allowed",
            marker_count,
            perplexity,
            classifier_score,
        )
