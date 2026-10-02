from __future__ import annotations

import math
import re

import httpx


PATTERNS = [
    r"ignore\s+(all|any|previous|prior)\s+instructions",
    r"system\s+prompt",
    r"developer\s+message",
    r"reveal\s+(your|the)\s+(prompt|instructions|secrets?)",
    r"send\s+(this|the)\s+(data|document|prompt)",
    r"disable\s+(safety|security|policy)",
    r"execute\s+.*(shell|command|code)",
    r"you\s+are\s+now\s+(the|a)",
]


class SecurityGateway:
    """Marker-based injection detection with optional vLLM PPL signal."""

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
            re.compile(
                pattern,
                re.IGNORECASE,
            )
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

        try:
            response = httpx.post(
                f"{self.base_url}/v1/completions",
                headers={
                    "Authorization": (
                        f"Bearer {self.api_key}"
                    )
                },
                json={
                    "model": self.model,
                    "prompt": text[:12000],
                    "max_tokens": 1,
                    "temperature": 0.0,
                    "prompt_logprobs": 1,
                },
                timeout=60,
            )
            response.raise_for_status()

            entries = (
                response.json()[
                    "choices"
                ][0].get(
                    "prompt_logprobs"
                )
                or []
            )

            values = []
            for entry in entries:
                if not isinstance(
                    entry,
                    dict,
                ):
                    continue

                for item in entry.values():
                    if not isinstance(
                        item,
                        dict,
                    ):
                        continue

                    logprob = item.get(
                        "logprob"
                    )

                    if isinstance(
                        logprob,
                        (int, float),
                    ):
                        values.append(
                            float(logprob)
                        )

            if not values:
                return None

            return float(
                math.exp(
                    -(
                        sum(values)
                        / len(values)
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

    def inspect(
        self,
        text: str,
        direct: bool = False,
    ) -> dict:
        marker_count = sum(
            len(
                pattern.findall(text)
            )
            for pattern in self.patterns
        )

        perplexity = self.perplexity(
            text
        )

        if direct and marker_count:
            return {
                "allowed": False,
                "reason": "direct injection marker",
                "marker_count": marker_count,
                "perplexity": perplexity,
            }

        if (
            marker_count
            >= self.marker_threshold
        ):
            return {
                "allowed": False,
                "reason": "retrieved injection markers",
                "marker_count": marker_count,
                "perplexity": perplexity,
            }

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
