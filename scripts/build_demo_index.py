from __future__ import annotations

import json
from pathlib import Path

from enterprise_graphrag.agent import build_agent
from enterprise_graphrag.config import settings


def load_documents() -> dict[str, list[dict]]:
    tenants: dict[str, list[dict]] = {}

    for line in Path(settings.corpus_path).read_text(
        encoding="utf-8"
    ).splitlines():
        line = line.strip()
        if not line:
            continue

        document = json.loads(line)
        tenants.setdefault(
            document["tenant_id"],
            [],
        ).append(
            {
                "doc_id": document["doc_id"],
                "title": document["title"],
                "text": document["text"],
            }
        )

    return tenants


def main() -> None:
    agent = build_agent()
    tenants = load_documents()

    for tenant_id, documents in tenants.items():
        agent.retriever.add(
            tenant_id,
            documents,
        )
        print(
            f"indexed tenant={tenant_id} "
            f"documents={len(documents)}"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "tenants": {
                    tenant: len(documents)
                    for tenant, documents in tenants.items()
                },
                "vector_backend": type(
                    agent.retriever.vector
                ).__name__,
                "graph_backend": type(
                    agent.retriever.graph
                ).__name__,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
