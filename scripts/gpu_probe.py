from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time

import httpx


def run_command(command: list[str]) -> str:
    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            + result.stdout
            + result.stderr
        )
    return result.stdout.strip()


def request_json(
    client: httpx.Client,
    method: str,
    url: str,
    **kwargs,
) -> tuple[dict, float]:
    started = time.perf_counter()
    response = client.request(method, url, **kwargs)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"{method} {url} returned non-object JSON"
        )
    return payload, elapsed_ms


def discover_model(
    client: httpx.Client,
    base_url: str,
    headers: dict[str, str],
    requested: str,
) -> str:
    payload, _ = request_json(
        client,
        "GET",
        f"{base_url}/v1/models",
        headers=headers,
    )
    items = payload.get("data")
    if not isinstance(items, list) or not items:
        raise RuntimeError("vLLM /v1/models returned no models")
    ids = [
        item.get("id")
        for item in items
        if isinstance(item, dict)
        and isinstance(item.get("id"), str)
        and item["id"].strip()
    ]
    if not ids:
        raise RuntimeError("vLLM /v1/models contained no usable model IDs")
    if requested:
        if requested not in ids:
            raise RuntimeError(
                f"requested vLLM model {requested!r} not present; available={ids}"
            )
        return requested
    return ids[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a CUDA A100 runner and a local OpenAI-compatible vLLM service."
    )
    parser.add_argument(
        "--vllm-base-url",
        default="http://127.0.0.1:8001",
    )
    parser.add_argument(
        "--vllm-api-key",
        default=os.getenv("VLLM_API_KEY", ""),
    )
    parser.add_argument(
        "--chat-model",
        default="",
        help="Optional exact model ID; defaults to the first model returned by /v1/models.",
    )
    parser.add_argument(
        "--embedding-base-url",
        default="",
        help="Optional OpenAI-compatible embedding service base URL.",
    )
    parser.add_argument(
        "--embedding-api-key",
        default=os.getenv("EMBEDDING_API_KEY", ""),
    )
    parser.add_argument(
        "--embedding-model",
        default="",
    )
    parser.add_argument(
        "--embedding-dimension",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--expected-gpu-name",
        default="A100",
    )
    parser.add_argument(
        "--output",
        default="gpu-validation.json",
    )
    args = parser.parse_args()

    if args.embedding_base_url and (
        not args.embedding_model or args.embedding_dimension < 1
    ):
        raise SystemExit(
            "--embedding-model and --embedding-dimension are required with --embedding-base-url"
        )

    report: dict[str, object] = {
        "vllm_base_url": args.vllm_base_url.rstrip("/"),
        "checks": {},
    }

    nvidia_smi = run_command(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits",
        ]
    )
    gpu_rows = []
    for line in nvidia_smi.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 5:
            continue
        gpu_rows.append(
            {
                "index": int(parts[0]),
                "name": parts[1],
                "memory_total_mib": int(parts[2]),
                "memory_used_mib": int(parts[3]),
                "utilization_percent": int(parts[4]),
            }
        )
    if not gpu_rows:
        raise RuntimeError("nvidia-smi returned no usable GPU rows")

    torch_code = (
        "import torch; "
        "print(torch.__version__); "
        "print(torch.cuda.is_available()); "
        "print(torch.cuda.device_count()); "
        "print([(torch.cuda.get_device_name(i), torch.cuda.get_device_capability(i)) "
        "for i in range(torch.cuda.device_count())])"
    )
    torch_output = run_command([sys.executable, "-c", torch_code])
    torch_lines = torch_output.splitlines()
    if len(torch_lines) < 4 or torch_lines[1].strip().lower() != "true":
        raise RuntimeError(
            "PyTorch does not report CUDA availability"
        )
    gpu_count = int(torch_lines[2].strip())
    if gpu_count < 1:
        raise RuntimeError("PyTorch reports zero CUDA devices")

    if args.expected_gpu_name:
        expected = args.expected_gpu_name.lower()
        if not any(expected in row["name"].lower() for row in gpu_rows):
            raise RuntimeError(
                "Expected GPU family not found: "
                f"expected={args.expected_gpu_name!r}, "
                f"actual={[row['name'] for row in gpu_rows]}"
            )

    report["checks"]["cuda"] = {
        "status": "ok",
        "nvidia_smi": gpu_rows,
        "torch_version": torch_lines[0],
        "cuda_available": True,
        "torch_gpu_count": gpu_count,
        "torch_devices": torch_lines[3],
    }

    headers = {"Content-Type": "application/json"}
    if args.vllm_api_key:
        headers["Authorization"] = f"Bearer {args.vllm_api_key}"

    base_url = args.vllm_base_url.rstrip("/")

    with httpx.Client(timeout=120.0) as client:
        models, models_ms = request_json(
            client,
            "GET",
            f"{base_url}/v1/models",
            headers=headers,
        )
        model = discover_model(
            client,
            base_url,
            headers,
            args.chat_model,
        )
        report["checks"]["models"] = {
            "status": "ok",
            "latency_ms": round(models_ms, 3),
            "selected_model": model,
            "available_models": [
                item.get("id")
                for item in models.get("data", [])
                if isinstance(item, dict)
            ],
        }

        chat, chat_ms = request_json(
            client,
            "POST",
            f"{base_url}/v1/chat/completions",
            headers=headers,
            json={
                "model": model,
                "temperature": 0.0,
                "max_tokens": 16,
                "messages": [
                    {
                        "role": "user",
                        "content": "Reply with a non-empty answer containing the word OK.",
                    }
                ],
            },
        )
        choices = chat.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("vLLM chat completion returned no choices")
        content = choices[0].get("message", {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("vLLM chat completion returned empty content")

        report["checks"]["chat"] = {
            "status": "ok",
            "latency_ms": round(chat_ms, 3),
            "response_nonempty": True,
        }

        completion, completion_ms = request_json(
            client,
            "POST",
            f"{base_url}/v1/completions",
            headers=headers,
            json={
                "model": model,
                "prompt": "Enterprise GraphRAG provider probe.",
                "max_tokens": 1,
                "temperature": 0.0,
                "prompt_logprobs": 1,
                "return_token_ids": True,
            },
        )
        completion_choices = completion.get("choices")
        if not isinstance(completion_choices, list) or not completion_choices:
            raise RuntimeError(
                "vLLM completion returned no choices"
            )
        choice = completion_choices[0]
        entries = choice.get("prompt_logprobs")
        token_ids = choice.get("prompt_token_ids")
        if not isinstance(entries, list) or not isinstance(token_ids, list):
            raise RuntimeError(
                "vLLM prompt-logprob response omitted prompt token data"
            )
        if len(entries) != len(token_ids):
            raise RuntimeError(
                "vLLM prompt-logprob token/logprob lengths differ"
            )

        observed = 0
        finite = True
        for position, entry in enumerate(entries):
            if position == 0 or entry is None:
                continue
            token_id = token_ids[position]
            token_data = entry.get(str(token_id))
            if token_data is None:
                token_data = entry.get(token_id)
            if not isinstance(token_data, dict):
                continue
            value = token_data.get("logprob")
            if isinstance(value, (int, float)):
                observed += 1
                finite = finite and math.isfinite(float(value))

        if observed < 1 or not finite:
            raise RuntimeError(
                "vLLM prompt-logprob response contained no finite observed-token logprobs"
            )

        report["checks"]["prompt_logprobs"] = {
            "status": "ok",
            "latency_ms": round(completion_ms, 3),
            "observed_token_logprobs": observed,
        }

        if args.embedding_base_url:
            embedding_url = args.embedding_base_url.rstrip("/")
            embedding_headers = {
                "Content-Type": "application/json"
            }
            if args.embedding_api_key:
                embedding_headers["Authorization"] = (
                    f"Bearer {args.embedding_api_key}"
                )

            embedding, embedding_ms = request_json(
                client,
                "POST",
                f"{embedding_url}/v1/embeddings",
                headers=embedding_headers,
                json={
                    "model": args.embedding_model,
                    "input": ["Enterprise GraphRAG GPU embedding probe."],
                },
            )
            items = embedding.get("data")
            if not isinstance(items, list) or not items:
                raise RuntimeError("embedding endpoint returned no data")
            vector = items[0].get("embedding")
            if not isinstance(vector, list):
                raise RuntimeError("embedding endpoint returned no vector")
            if len(vector) != args.embedding_dimension:
                raise RuntimeError(
                    "embedding dimension mismatch: "
                    f"expected={args.embedding_dimension}, actual={len(vector)}"
                )
            if not all(
                isinstance(value, (int, float))
                and math.isfinite(float(value))
                for value in vector
            ):
                raise RuntimeError(
                    "embedding endpoint returned non-finite values"
                )

            report["checks"]["embeddings"] = {
                "status": "ok",
                "latency_ms": round(embedding_ms, 3),
                "dimension": len(vector),
            }

    report["status"] = "ok"
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
