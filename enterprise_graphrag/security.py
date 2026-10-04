from __future__ import annotations

import math
import re
import unicodedata

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
    """Marker-based injection detection with an optional exact prompt-PPL signal."""

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = "",
        threshold: float = 80.0,
        marker_threshold: int = 2,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.threshold = threshold
        self.marker_threshold = marker_threshold
        self.patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in PATTERNS
        ]

    def perplexity(
        self,
        text: str,
    ) -> float | None:
        if not (
            self.base_url
            and self.model
        ):
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

            choice = response.json()[
                "choices"
            ][0]
            entries = (
                choice.get(
                    "prompt_logprobs"
                )
                or []
            )
            token_ids = (
                choice.get(
                    "prompt_token_ids"
                )
                or []
            )

            if len(entries) != len(token_ids):
                return None

            observed = []

            for position, entry in enumerate(
                entries
            ):
                if (
                    position == 0
                    or entry is None
                ):
                    continue

                token_id = token_ids[position]
                token_data = entry.get(
                    str(token_id)
                )

                if token_data is None:
                    token_data = entry.get(
                        token_id
                    )

                if not isinstance(
                    token_data,
                    dict,
                ):
                    continue

                logprob = token_data.get(
                    "logprob"
                )

                if isinstance(
                    logprob,
                    (int, float),
                ):
                    observed.append(
                        float(logprob)
                    )

            if not observed:
                return None

            return float(
                math.exp(
                    -(
                        sum(observed)
                        / len(observed)
                    )
                )
            )

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
        # Normalize compatibility characters and strip zero-width controls so
        # obvious prompt-injection phrases cannot evade marker detection by
        # Unicode formatting tricks.
        normalized = unicodedata.normalize(
            "NFKC",
            text,
        )
        return "".join(
            char
            for char in normalized
            if char not in "\u200b\u200c\u200d\ufeff"
        )

    def inspect(
        self,
        text: str,
        direct: bool = False,
    ) -> dict:
        text = self._normalize(text)
        marker_count = sum(
            len(
                pattern.findall(text)
            )
            for pattern in self.patterns
        )

        if direct and marker_count:
            return {
                "allowed": False,
                "reason": "direct injection marker",
                "marker_count": marker_count,
                "perplexity": None,
            }

        if marker_count >= self.marker_threshold:
            return {
                "allowed": False,
                "reason": "retrieved injection markers",
                "marker_count": marker_count,
                "perplexity": None,
            }

        perplexity = self.perplexity(
            text
        )

        if (
            perplexity is not None
            and perplexity >= self.threshold
            and marker_count >= 1
        ):
            return {
                "allowed": False,
                "reason": "high perplexity plus injection marker",
                "marker_count": marker_count,
                "perplexity": perplexity,
            }

        return {
            "allowed": True,
            "reason": "allowed",
            "marker_count": marker_count,
            "perplexity": perplexity,
        }
