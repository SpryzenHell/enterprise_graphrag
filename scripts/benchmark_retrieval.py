from __future__ import annotations

import json
import tempfile
from pathlib import Path

from enterprise_graphrag.embeddings import HashEmbedder
from enterprise_graphrag.retrieval import HybridRetriever, TenantMemoryGraph
from enterprise_graphrag.security import SecurityGateway
from enterprise_graphrag.vector_faiss import TenantFAISS


def load_fixture():
    corpus = {}

    for line in Path("enterprise_data/corpus.jsonl").read_text(
        encoding="utf-8"
    ).splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        corpus.setdefault(item["tenant_id"], []).append(
            item
        )

    questions = json.loads(
        Path("enterprise_data/eval_questions.json").read_text(
            encoding="utf-8"
        )
    )
    return corpus, questions


def reciprocal_rank(hits, expected_doc_id: str) -> float:
    for rank, hit in enumerate(hits, start=1):
        if hit.doc_id == expected_doc_id:
            return 1.0 / rank
    return 0.0


def main() -> None:
    corpus, questions = load_fixture()

    root = Path(
        tempfile.mkdtemp(
            prefix="enterprise-graphrag-benchmark-"
        )
    )
    vector = TenantFAISS(
        str(root),
        HashEmbedder(128),
    )
    graph = TenantMemoryGraph()
    security = SecurityGateway(
        threshold=80,
        marker_threshold=2,
    )
    retriever = HybridRetriever(
        vector=vector,
        graph=graph,
        security=security,
        vector_weight=0.55,
        graph_weight=0.45,
        rrf_k=60,
    )

    for tenant, documents in corpus.items():
        retriever.add(tenant, documents)

    k = 5
    metrics = {
        "k": k,
        "questions": len(questions),
        "vector": {"hits": 0, "mrr": 0.0},
        "graph": {"hits": 0, "mrr": 0.0},
        "hybrid_rrf": {"hits": 0, "mrr": 0.0},
    }

    for question in questions:
        tenant = question["tenant_id"]
        query = question["query"]
        expected = question["expected_doc_id"]

        vector_hits = retriever.vector.search(
            tenant,
            query,
            k,
        )
        graph_hits = retriever.graph.search(
            tenant,
            query,
            k,
        )
        hybrid_hits, _, _, _ = retriever.search(
            tenant,
            query,
            k,
        )

        for name, hits in (
            ("vector", vector_hits),
            ("graph", graph_hits),
            ("hybrid_rrf", hybrid_hits),
        ):
            rr = reciprocal_rank(
                hits,
                expected,
            )
            metrics[name]["mrr"] += rr
            metrics[name]["hits"] += int(rr > 0)

    count = max(metrics["questions"], 1)
    for name in ("vector", "graph", "hybrid_rrf"):
        metrics[name]["recall_at_5"] = (
            metrics[name]["hits"] / count
        )
        metrics[name]["mrr"] = (
            metrics[name]["mrr"] / count
        )

    output = Path(
        "enterprise_data/benchmark.json"
    )
    output.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
