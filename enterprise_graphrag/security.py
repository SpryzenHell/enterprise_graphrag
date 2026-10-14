from __future__ import annotations

import math
import re
import unicodedata
from collections.abc import Callable

import httpx


PATTERNS = [
    r"ignore\s+(?:(?:all|any)\s+)?(?:(?:previous|prior)\s+)?instructions",
    r"system\s+prompt",
    r"developer\s+message",
    r"reveal\s+(your|the)\s+(prompt|instructions|secrets?)",
    r"send\s+(this|the)\s+(data|document|prompt)",
    r"disable\s+(safety|security|policy)",
    r"execute\s+.*(shell|command|code)",
    r"you\s+are\s+now\s+(the|a)",
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
        classifier_window_overlap: int = 512,
        classifier_score_fn: Callable[[str], float] | None = None,
        ppl_min_classifier_score: float = 0.10,
    ) -> None:
        if marker_threshold < 1:
            raise ValueError("marker_threshold must be at least 1")
        if not 0.0 <= classifier_threshold <= 1.0:
            raise ValueError("classifier_threshold must be between 0 and 1")
        if not 0.0 <= ppl_min_classifier_score <= 1.0:
            raise ValueError("ppl_min_classifier_score must be between 0 and 1")
        if classifier_max_length < 8 or classifier_max_length > 8192:
            raise ValueError("classifier_max_length must be between 8 and 8192")
        if classifier_window_overlap < 0 or classifier_window_overlap >= classifier_max_length - 2:
            raise ValueError("classifier_window_overlap must be non-negative and smaller than classifier_max_length - 2")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.threshold = threshold
        self.marker_threshold = marker_threshold
        self.ppl_min_classifier_score = float(ppl_min_classifier_score)
        self.classifier_model = classifier_model.strip()
        self.classifier_threshold = float(classifier_threshold)
        self.classifier_max_length = int(classifier_max_length)
        self.classifier_window_overlap = int(classifier_window_overlap)
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

    def _semantic_scores(self, texts: list[str]) -> list[float]:
        if not texts:
            return []
        if self._classifier_score_fn is not None:
            scores = [float(self._classifier_score_fn(text)) for text in texts]
        else:
            if not (
                self._classifier_enabled
                and self._classifier_tokenizer is not None
                and self._classifier is not None
                and self._classifier_torch is not None
            ):
                raise RuntimeError("semantic classifier was enabled but is not initialized")

            tokenizer = self._classifier_tokenizer
            torch = self._classifier_torch
            special_tokens = int(tokenizer.num_special_tokens_to_add(pair=False))
            content_limit = self.classifier_max_length - special_tokens
            step = content_limit - self.classifier_window_overlap
            windows: list[dict] = []
            owners: list[int] = []

            # Scan the complete input. Truncating only the prefix could miss an injected
            # instruction deliberately placed near the end of a long retrieved document.
            for owner, text in enumerate(texts):
                token_ids = tokenizer.encode(
                    text,
                    add_special_tokens=False,
                    truncation=False,
                )
                starts = [0]
                if len(token_ids) > content_limit:
                    starts = list(range(0, len(token_ids), step))
                    last_start = max(0, len(token_ids) - content_limit)
                    if starts[-1] < last_start:
                        starts.append(last_start)
                for start in starts:
                    content = token_ids[start:start + content_limit]
                    encoded = tokenizer.prepare_for_model(
                        content,
                        add_special_tokens=True,
                        truncation=True,
                        max_length=self.classifier_max_length,
                        return_attention_mask=True,
                    )
                    windows.append(encoded)
                    owners.append(owner)
                    if start + content_limit >= len(token_ids):
                        break

            window_scores: list[list[float]] = [[] for _ in texts]
            batch_size = 16
            for offset in range(0, len(windows), batch_size):
                batch = tokenizer.pad(
                    windows[offset:offset + batch_size],
                    padding=True,
                    return_tensors="pt",
                )
                batch = {
                    key: value.to(self._classifier_device)
                    for key, value in batch.items()
                }
                with torch.inference_mode():
                    logits = self._classifier(**batch).logits.float()
                    probs = torch.softmax(logits, dim=-1)[:, self._positive_class_index]
                    values = [float(value) for value in probs.detach().cpu().tolist()]
                for owner, value in zip(owners[offset:offset + batch_size], values):
                    window_scores[owner].append(value)
            # Model guidance for long inputs is max-over-windows: any malicious region
            # must be sufficient to block the passage, regardless of where it occurs.
            scores = [max(values, default=0.0) for values in window_scores]

        if len(scores) != len(texts):
            raise ValueError("semantic classifier returned the wrong number of probabilities")
        if any(not math.isfinite(score) or not 0.0 <= score <= 1.0 for score in scores):
            raise ValueError("semantic classifier returned an invalid probability")
        return scores

    def _semantic_score(self, text: str) -> float:
        return self._semantic_scores([text])[0]

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
                    "max_tokens": 0,
                    "temperature": 0.0,
                    "echo": True,
                    "logprobs": 1,
                    "prompt_logprobs": 1,
                    "return_token_ids": True,
                },
                timeout=60,
            )
            response.raise_for_status()
            choice = response.json()["choices"][0]
            entries = choice.get("prompt_logprobs") or []
            token_ids = choice.get("prompt_token_ids") or []
            observed = []
            if isinstance(entries, list) and isinstance(token_ids, list) and len(entries) == len(token_ids):
                for position, entry in enumerate(entries):
                    if position == 0 or entry is None or not isinstance(entry, dict):
                        continue
                    token_id = token_ids[position]
                    token_data = entry.get(str(token_id))
                    if token_data is None:
                        token_data = entry.get(token_id)
                    if not isinstance(token_data, dict):
                        continue
                    logprob = token_data.get("logprob")
                    if isinstance(logprob, (int, float)) and math.isfinite(float(logprob)):
                        observed.append(float(logprob))

            # Older vLLM builds may accept prompt_logprobs but omit the optional
            # prompt_token_ids response field. With echo=True and logprobs=1,
            # OpenAI-compatible completions return the observed token's own
            # logprob sequence; prefer that over confusing top-k alternatives
            # with the token actually present in the prompt.
            if not observed:
                logprob_payload = choice.get("logprobs") or {}
                token_logprobs = logprob_payload.get("token_logprobs") or []
                if isinstance(token_logprobs, list):
                    observed = [
                        float(value)
                        for value in token_logprobs
                        if isinstance(value, (int, float)) and math.isfinite(float(value))
                    ]

            if not observed:
                return None
            try:
                score = float(math.exp(-(sum(observed) / len(observed))))
                return score if math.isfinite(score) else None
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
            if char not in "\u200b\u200c\u200d\ufeff"
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
        return self.inspect_many([text], direct=direct)[0]

    def inspect_many(self, texts: list[str], direct: bool = False) -> list[dict]:
        """Inspect several untrusted passages with one batched classifier forward pass."""
        normalized = [self._normalize(text) for text in texts]
        decisions: list[dict | None] = [None] * len(normalized)
        marker_counts = [
            sum(len(pattern.findall(text)) for pattern in self.patterns)
            for text in normalized
        ]
        pending: list[int] = []

        for index, marker_count in enumerate(marker_counts):
            if direct and marker_count:
                decisions[index] = self._decision(False, "direct injection marker", marker_count)
            elif marker_count >= self.marker_threshold:
                decisions[index] = self._decision(False, "retrieved injection markers", marker_count)
            else:
                pending.append(index)

        classifier_scores: dict[int, float] = {}
        if self._classifier_enabled and pending:
            try:
                scores = self._semantic_scores([normalized[index] for index in pending])
                for index, score in zip(pending, scores):
                    classifier_scores[index] = score
            except Exception:
                # An explicitly configured detector must not silently fail open.
                for index in pending:
                    decisions[index] = self._decision(
                        False,
                        "semantic injection classifier failure (blocked closed)",
                        marker_counts[index],
                    )
                pending = []

        after_classifier: list[int] = []
        for index in pending:
            score = classifier_scores.get(index)
            if score is not None and score >= self.classifier_threshold:
                decisions[index] = self._decision(
                    False,
                    "semantic injection classifier",
                    marker_counts[index],
                    classifier_score=score,
                )
            else:
                after_classifier.append(index)

        # PPL is a second-stage discriminator, not a standalone policy: the
        # A100 sweep showed high perplexity alone flags too many benign documents.
        # Call it for marker-positive text or semantically borderline text, where
        # it can add evidence while avoiding a costly request for every clean passage.
        for index in after_classifier:
            marker_count = marker_counts[index]
            classifier_score = classifier_scores.get(index)
            borderline_semantic = (
                classifier_score is not None
                and self.ppl_min_classifier_score <= classifier_score < self.classifier_threshold
            )
            ppl_eligible = marker_count >= 1 or borderline_semantic
            ppl_configured = bool(self.base_url and self.model)
            perplexity = self.perplexity(normalized[index]) if ppl_eligible else None
            if ppl_eligible and ppl_configured and perplexity is None:
                # Do not silently accept content that was routed to the second-stage
                # security check when the configured scorer timed out, returned a
                # malformed response, or produced no usable token likelihoods.
                decisions[index] = self._decision(
                    False,
                    "perplexity evaluation unavailable (blocked closed)",
                    marker_count,
                    None,
                    classifier_score,
                )
            elif perplexity is not None and perplexity >= self.threshold and ppl_eligible:
                reason = (
                    "high perplexity plus injection marker"
                    if marker_count >= 1
                    else "high perplexity in borderline semantic region"
                )
                decisions[index] = self._decision(
                    False,
                    reason,
                    marker_count,
                    perplexity,
                    classifier_score,
                )
            else:
                decisions[index] = self._decision(
                    True,
                    "allowed",
                    marker_count,
                    perplexity,
                    classifier_score,
                )

        return [decision if decision is not None else self._decision(False, "security decision unavailable", marker_counts[index]) for index, decision in enumerate(decisions)]
