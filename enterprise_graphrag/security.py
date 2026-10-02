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
]


class SecurityGateway:
    def __init__(self, base_url: str = "", api_key: str = "", model: str = "", threshold: float = 80.0, marker_threshold: int = 2):
        self.base_url, self.api_key, self.model = base_url.rstrip("/"), api_key, model
        self.threshold, self.marker_threshold = threshold, marker_threshold
        self.patterns = [re.compile(p, re.I) for p in PATTERNS]

    def perplexity(self, text: str) -> float | None:
        if not (self.base_url and self.model):
            return None
        try:
            r = httpx.post(f"{self.base_url}/v1/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json={"model": self.model, "prompt": text[:12000], "max_tokens": 1, "temperature": 0, "prompt_logprobs": 1}, timeout=60)
            r.raise_for_status()
            items = r.json()["choices"][0].get("prompt_logprobs") or []
            values = []
            for item in items:
                if isinstance(item, dict):
                    for value in item.values():
                        if isinstance(value, dict) and isinstance(value.get("logprob"), (int, float)):
                            values.append(float(value["logprob"]))
            return math.exp(-(sum(values) / len(values))) if values else None
        except (OSError, httpx.HTTPError, KeyError, TypeError, ValueError):
            return None

    def inspect(self, text: str, direct: bool = False) -> dict:
        markers = sum(len(p.findall(text)) for p in self.patterns)
        ppl = self.perplexity(text)
        if markers and direct:
            return {"allowed": False, "reason": "direct injection marker", "marker_count": markers, "perplexity": ppl}
        if markers >= self.marker_threshold:
            return {"allowed": False, "reason": "retrieved injection markers", "marker_count": markers, "perplexity": ppl}
        if ppl is not None and ppl >= self.threshold and markers:
            return {"allowed": False, "reason": "high perplexity plus injection marker", "marker_count": markers, "perplexity": ppl}
        return {"allowed": True, "reason": "allowed", "marker_count": markers, "perplexity": ppl}
