from __future__ import annotations

import argparse
import json
import math
import time

import httpx


def timed_post(
    client: httpx.Client,
    url: str,
    **kwargs,
) -> tuple[httpx.Response, float]:
    started = time.perf_counter()
    response = client.post(url, **kwargs)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()
    return response, elapsed_ms


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe a real OpenAI-compatible inference provider."
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Provider base URL without the /v1 suffix.",
    )
    parser.add_argument(
        "--api-key",
        default="",
        help="Optional provider API key; omit for local unauthenticated vLLM.",
    )
    parser.add_argument(
        "--chat-model",
        required=True,
    )
    parser.add_argument(
        "--embedding-model",
        required=True,
    )
    parser.add_argument(
        "--embedding-dimension",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--prompt",
        default="Reply with the single word OK.",
    )
    args = parser.parse_args()

    if args.embedding_dimension < 1:
        raise SystemExit("--embedding-dimension must be at least 1")

    base_url = args.base_url.rstrip("/")
    headers = {"Content-Type": "application/json"}
    if args.api_key:
        headers["Authorization"] = f"Bearer {args.api_key}"

    report: dict[str, object] = {
        "base_url": base_url,
        "chat_model": args.chat_model,
        "embedding_model": args.embedding_model,
        "checks": {},
    }

    with httpx.Client(timeout=120.0) as client:
        chat, chat_ms = timed_post(
            client,
            f"{base_url}/v1/chat/completions",
            headers=headers,
            json={
                "model": args.chat_model,
                "temperature": 0.0,
                "max_tokens": 16,
                "messages": [
                    {
                        "role": "user",
                        "content": args.prompt,
                    }
                ],
            },
        )
        chat_payload = chat.json()
        choices = chat_payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError(
                "Chat completion returned no choices"
            )
        chat_content = choices[0].get("message", {}).get("content")
        if not isinstance(chat_content, str) or not chat_content.strip():
            raise RuntimeError(
                "Chat completion returned no message content"
            )
        report["checks"]["chat"] = {
            "status": "ok",
            "latency_ms": round(chat_ms, 3),
            "response": chat_content,
        }

        embedding, embedding_ms = timed_post(
            client,
            f"{base_url}/v1/embeddings",
            headers=headers,
            json={
                "model": args.embedding_model,
                "input": ["Enterprise GraphRAG provider probe."],
            },
        )
        embedding_payload = embedding.json()
        items = embedding_payload.get("data")
        if not isinstance(items, list) or not items:
            raise RuntimeError(
                "Embedding endpoint returned no data"
            )
        vector = items[0].get("embedding")
        if not isinstance(vector, list):
            raise RuntimeError(
                "Embedding endpoint returned an invalid vector"
            )
        actual_dimension = len(vector)
        if actual_dimension != args.embedding_dimension:
            raise RuntimeError(
                "Embedding dimension mismatch: "
                f"configured={args.embedding_dimension}, "
                f"actual={actual_dimension}"
            )
        if not all(
            isinstance(value, (int, float))
            and math.isfinite(float(value))
            for value in vector
        ):
            raise RuntimeError(
                "Embedding endpoint returned non-finite values"
            )
        report["checks"]["embeddings"] = {
            "status": "ok",
            "latency_ms": round(embedding_ms, 3),
            "dimension": actual_dimension,
        }

        ppl, ppl_ms = timed_post(
            client,
            f"{base_url}/v1/completions",
            headers=headers,
            json={
                "model": args.chat_model,
                "prompt": "Enterprise GraphRAG provider probe.",
                "max_tokens": 1,
                "temperature": 0.0,
                "prompt_logprobs": 1,
                "return_token_ids": True,
            },
        )
        ppl_payload = ppl.json()
        ppl_choices = ppl_payload.get("choices")
        if not isinstance(ppl_choices, list) or not ppl_choices:
            raise RuntimeError(
                "Prompt-logprob endpoint returned no choices"
            )
        choice = ppl_choices[0]
        entries = choice.get("prompt_logprobs")
        token_ids = choice.get("prompt_token_ids")
        if not isinstance(entries, list) or not isinstance(token_ids, list):
            raise RuntimeError(
                "Prompt-logprob response is missing prompt token data"
            )
        if len(entries) != len(token_ids):
            raise RuntimeError(
                "Prompt-logprob token/logprob lengths differ"
            )

        observed = 0
        for position, entry in enumerate(entries):
            if position == 0 or entry is None:
                continue
            token_id = token_ids[position]
            token_data = entry.get(str(token_id))
            if token_data is None:
                token_data = entry.get(token_id)
            if isinstance(token_data, dict) and isinstance(
                token_data.get("logprob"),
                (int, float),
            ):
                observed += 1

        if observed == 0:
            raise RuntimeError(
                "Prompt-logprob response contained no observed-token logprobs"
            )

        report["checks"]["prompt_logprobs"] = {
            "status": "ok",
            "latency_ms": round(ppl_ms, 3),
            "observed_token_logprobs": observed,
        }

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
