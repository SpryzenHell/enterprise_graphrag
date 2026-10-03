from __future__ import annotations

import argparse
import json
import time

import httpx


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
            f"{method} {url} returned a non-object JSON payload"
        )
    return payload, elapsed_ms


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe a running Enterprise GraphRAG HTTP deployment."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
    )
    parser.add_argument(
        "--token",
        default="",
    )
    parser.add_argument(
        "--tenant",
        default="",
    )
    parser.add_argument(
        "--query",
        default="",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    headers = (
        {"Authorization": f"Bearer {args.token}"}
        if args.token
        else {}
    )

    results: dict[str, object] = {
        "base_url": base_url,
        "checks": {},
    }

    with httpx.Client(
        timeout=args.timeout,
    ) as client:
        health, health_ms = request_json(
            client,
            "GET",
            f"{base_url}/health",
        )
        if health.get("status") != "ok":
            raise RuntimeError(
                f"Health check returned unexpected status: {health.get('status')!r}"
            )
        results["checks"]["health"] = {
            "status": health.get("status"),
            "latency_ms": round(health_ms, 3),
            "mcp_enabled": health.get("mcp_enabled"),
        }

        ready, ready_ms = request_json(
            client,
            "GET",
            f"{base_url}/ready",
        )
        if ready.get("status") != "ready":
            raise RuntimeError(
                f"Readiness check returned unexpected status: {ready.get('status')!r}"
            )
        results["checks"]["ready"] = {
            "status": ready.get("status"),
            "latency_ms": round(ready_ms, 3),
            "graph_backend": ready.get("graph_backend"),
            "vector_backend": ready.get("vector_backend"),
        }

        if args.token:
            tenant, tenant_ms = request_json(
                client,
                "GET",
                f"{base_url}/v1/tenant",
                headers=headers,
            )
            results["checks"]["tenant"] = {
                "status": "ok",
                "latency_ms": round(tenant_ms, 3),
                "tenant_id": tenant.get("tenant_id"),
            }
            if args.tenant and tenant.get("tenant_id") != args.tenant:
                raise RuntimeError(
                    "Authenticated tenant mismatch: "
                    f"expected={args.tenant}, actual={tenant.get('tenant_id')}"
                )

            if args.query:
                answer, query_ms = request_json(
                    client,
                    "POST",
                    f"{base_url}/v1/query",
                    headers={
                        **headers,
                        "Content-Type": "application/json",
                    },
                    json={"query": args.query},
                )
                citations = answer.get("citations", [])
                if not isinstance(citations, list):
                    raise RuntimeError(
                        "Query response citations must be a list"
                    )

                if args.tenant:
                    leaked = [
                        citation
                        for citation in citations
                        if citation.get("tenant_id") != args.tenant
                    ]
                    if leaked:
                        raise RuntimeError(
                            "Cross-tenant citations detected: "
                            + json.dumps(leaked)
                        )

                results["checks"]["query"] = {
                    "status": "ok",
                    "latency_ms": round(query_ms, 3),
                    "citation_count": len(citations),
                    "security_allowed": (
                        answer.get("security", {}).get("allowed")
                    ),
                }

    print(
        json.dumps(
            results,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
