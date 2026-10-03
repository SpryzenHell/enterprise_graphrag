from __future__ import annotations

import argparse
import json

import httpx


def rpc(
    client: httpx.Client,
    url: str,
    headers: dict[str, str],
    request_id: int,
    method: str,
    params: dict,
) -> dict:
    response = client.post(
        url,
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        },
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(
            f"{method} returned a non-object JSON response"
        )
    if "error" in payload:
        raise RuntimeError(
            f"{method} returned an MCP error: "
            + json.dumps(payload["error"])
        )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe an authenticated Streamable HTTP MCP endpoint."
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000/mcp/",
    )
    parser.add_argument(
        "--token",
        required=True,
    )
    parser.add_argument(
        "--tenant",
        required=True,
    )
    parser.add_argument(
        "--query",
        default="incident records",
    )
    parser.add_argument(
        "--expected-doc-id",
        default="",
    )
    args = parser.parse_args()

    headers = {
        "Authorization": f"Bearer {args.token}",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "Mcp-Protocol-Version": "2025-06-18",
    }

    report: dict[str, object] = {
        "url": args.url,
        "tenant": args.tenant,
        "checks": {},
    }

    with httpx.Client(
        timeout=30.0,
    ) as client:
        initialize = rpc(
            client,
            args.url,
            headers,
            1,
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "enterprise-graphrag-probe",
                    "version": "0.1.0",
                },
            },
        )
        report["checks"]["initialize"] = {
            "status": "ok",
            "protocol_version": initialize["result"].get(
                "protocolVersion"
            ),
        }

        notify = client.post(
            args.url,
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            },
        )
        if notify.status_code not in {200, 202}:
            notify.raise_for_status()
        report["checks"]["initialized_notification"] = {
            "status": "ok",
            "http_status": notify.status_code,
        }

        listed = rpc(
            client,
            args.url,
            headers,
            2,
            "tools/list",
            {},
        )
        tools = listed["result"].get("tools", [])
        tool_names = [
            item.get("name")
            for item in tools
            if isinstance(item, dict)
        ]
        if "hybrid_search" not in tool_names:
            raise RuntimeError(
                "hybrid_search was not advertised by the MCP server"
            )
        report["checks"]["tools"] = {
            "status": "ok",
            "tools": tool_names,
        }

        called = rpc(
            client,
            args.url,
            headers,
            3,
            "tools/call",
            {
                "name": "hybrid_search",
                "arguments": {
                    "query": args.query,
                    "top_k": 8,
                },
            },
        )
        result = called["result"]
        if result.get("isError") is True:
            raise RuntimeError(
                "hybrid_search returned an MCP tool error"
            )
        structured = result.get("structuredContent") or {}
        trace = structured.get("trace") or {}
        if trace.get("tenant_id") != args.tenant:
            raise RuntimeError(
                "MCP tool returned the wrong tenant: "
                + repr(trace.get("tenant_id"))
            )

        citations = structured.get("citations") or []
        if not isinstance(citations, list):
            raise RuntimeError(
                "MCP hybrid_search citations must be a list"
            )
        leaked = [
            citation
            for citation in citations
            if citation.get("tenant_id") != args.tenant
        ]
        if leaked:
            raise RuntimeError(
                "MCP returned cross-tenant citations: "
                + json.dumps(leaked)
            )
        if args.expected_doc_id and not any(
            citation.get("doc_id") == args.expected_doc_id
            for citation in citations
        ):
            raise RuntimeError(
                "Expected MCP citation was not returned: "
                + args.expected_doc_id
            )

        report["checks"]["hybrid_search"] = {
            "status": "ok",
            "citation_count": len(citations),
            "tenant_id": trace.get("tenant_id"),
        }

    print(
        json.dumps(
            report,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
