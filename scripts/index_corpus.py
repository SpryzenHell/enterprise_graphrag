from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from enterprise_graphrag.agent import build_agent
from enterprise_graphrag.config import settings


def iter_documents(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                document = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid JSON on line {line_number} of {path}"
                ) from exc

            if not isinstance(document, dict):
                raise ValueError(
                    f"line {line_number} of {path} is not a JSON object"
                )

            tenant_id = document.get("tenant_id")
            if not isinstance(tenant_id, str) or not tenant_id.strip():
                raise ValueError(
                    f"line {line_number} of {path} is missing tenant_id"
                )

            yield tenant_id, {
                key: value
                for key, value in document.items()
                if key != "tenant_id"
            }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stream a tenant-partitioned JSONL corpus into GraphRAG."
    )
    parser.add_argument(
        "--corpus",
        default=settings.corpus_path,
        help="JSONL corpus path; defaults to GRAGRAPH_CORPUS.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Documents per tenant batch before ingestion.",
    )
    parser.add_argument(
        "--tenant",
        action="append",
        default=[],
        help="Optional tenant allowlist; repeat for multiple tenants.",
    )
    args = parser.parse_args()

    if args.batch_size < 1 or args.batch_size > 1000:
        raise SystemExit("--batch-size must be between 1 and 1000")

    tenant_filter = set(args.tenant)
    path = Path(args.corpus)
    if not path.is_file():
        raise SystemExit(f"Corpus does not exist: {path}")

    agent = build_agent()
    batches: dict[str, list[dict]] = defaultdict(list)
    totals: dict[str, int] = defaultdict(int)

    def flush(tenant_id: str) -> None:
        documents = batches[tenant_id]
        if not documents:
            return
        agent.retriever.add(tenant_id, documents)
        totals[tenant_id] += len(documents)
        print(
            f"indexed tenant={tenant_id} batch={len(documents)} total={totals[tenant_id]}",
            flush=True,
        )
        batches[tenant_id].clear()

    for tenant_id, document in iter_documents(path):
        if tenant_filter and tenant_id not in tenant_filter:
            continue

        batches[tenant_id].append(document)
        if len(batches[tenant_id]) >= args.batch_size:
            flush(tenant_id)

    for tenant_id in sorted(batches):
        flush(tenant_id)

    print(
        json.dumps(
            {
                "status": "ok",
                "corpus": str(path),
                "batch_size": args.batch_size,
                "tenants": dict(sorted(totals.items())),
                "documents_indexed": sum(totals.values()),
                "vector_backend": type(agent.retriever.vector).__name__,
                "graph_backend": type(agent.retriever.graph).__name__,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
