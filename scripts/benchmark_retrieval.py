from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path

from enterprise_graphrag.embeddings import HashEmbedder
from enterprise_graphrag.retrieval import (
    HybridRetriever,
    TenantMemoryGraph,
)
from enterprise_graphrag.security import SecurityGateway
from enterprise_graphrag.vector_faiss import TenantFAISS


def load_fixture(
    corpus_path: str,
    questions_path: str,
):
    corpus = {}

    for line in Path(
        corpus_path
    ).read_text(
        encoding="utf-8"
    ).splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        corpus.setdefault(
            item["tenant_id"],
            [],
        ).append(item)

    questions = json.loads(
        Path(
            questions_path
        ).read_text(
            encoding="utf-8"
        )
    )
    return corpus, questions


def reciprocal_rank(
    hits,
    expected_doc_id: str,
) -> float:
    for rank, hit in enumerate(
        hits,
        start=1,
    ):
        if hit.doc_id == expected_doc_id:
            return 1.0 / rank
    return 0.0


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(
        int((len(ordered) - 1) * fraction),
        len(ordered) - 1,
    )
    return float(ordered[index])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark tenant-scoped vector, graph, and hybrid retrieval."
    )
    parser.add_argument(
        "--corpus",
        default="enterprise_data/corpus.jsonl",
    )
    parser.add_argument(
        "--questions",
        default="enterprise_data/eval_questions.json",
    )
    parser.add_argument(
        "--output",
        default="enterprise_data/benchmark.json",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
    )
    args = parser.parse_args()

    if args.k < 1:
        raise SystemExit("--k must be at least 1")

    corpus, questions = load_fixture(
        args.corpus,
        args.questions,
    )

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
        retriever.add(
            tenant,
            documents,
        )

    k = args.k
    latency = {
        "vector_ms": [],
        "graph_ms": [],
        "hybrid_rrf_ms": [],
    }
    metrics = {
        "dataset": str(args.questions),
        "k": k,
        "questions": len(questions),
        "vector": {
            "hits": 0,
            "mrr": 0.0,
        },
        "graph": {
            "hits": 0,
            "mrr": 0.0,
        },
        "hybrid_rrf": {
            "hits": 0,
            "mrr": 0.0,
        },
    }

    for question in questions:
        tenant = question["tenant_id"]
        query = question["query"]
        expected = question["expected_doc_id"]

        start = time.perf_counter()
        vector_hits = retriever.vector.search(
            tenant,
            query,
            k,
        )
        latency["vector_ms"].append(
            (time.perf_counter() - start) * 1000
        )

        start = time.perf_counter()
        graph_hits = retriever.graph.search(
            tenant,
            query,
            k,
        )
        latency["graph_ms"].append(
            (time.perf_counter() - start) * 1000
        )

        start = time.perf_counter()
        hybrid_hits, _, _, _ = retriever.search(
            tenant,
            query,
            k,
        )
        latency["hybrid_rrf_ms"].append(
            (time.perf_counter() - start) * 1000
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
            metrics[name]["hits"] += int(
                rr > 0
            )

    count = max(
        metrics["questions"],
        1,
    )

    for name in (
        "vector",
        "graph",
        "hybrid_rrf",
    ):
        metrics[name]["recall_at_5"] = (
            metrics[name]["hits"] / count
        )
        metrics[name]["mrr"] = (
            metrics[name]["mrr"] / count
        )

    metrics["latency_ms"] = {
        name: {
            "p50": percentile(values, 0.50),
            "p95": percentile(values, 0.95),
            "max": max(values, default=0.0),
        }
        for name, values in latency.items()
    }

    output = Path(args.output)
    output.write_text(
        json.dumps(
            metrics,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            metrics,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
