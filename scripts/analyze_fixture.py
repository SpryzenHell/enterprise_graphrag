from __future__ import annotations

import argparse
import json
import math
import tempfile
import time
from pathlib import Path

from enterprise_graphrag.embeddings import HashEmbedder
from enterprise_graphrag.retrieval import HybridRetriever, TenantMemoryGraph
from enterprise_graphrag.security import SecurityGateway
from enterprise_graphrag.vector_faiss import TenantFAISS


def load_corpus(path: Path) -> dict[str, list[dict]]:
    corpus: dict[str, list[dict]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        corpus.setdefault(item["tenant_id"], []).append(item)
    return corpus


def load_questions(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def reciprocal_rank(hits, expected_doc_id: str) -> float:
    for rank, hit in enumerate(hits, start=1):
        if hit.doc_id == expected_doc_id:
            return 1.0 / rank
    return 0.0


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * fraction), len(ordered) - 1)
    return float(ordered[index])


def timed(call):
    started = time.perf_counter()
    value = call()
    elapsed_ms = (time.perf_counter() - started) * 1000
    return value, elapsed_ms


def evaluate_retrieval(retriever: HybridRetriever, questions: list[dict], k: int):
    methods = ("vector", "graph", "hybrid")
    metrics = {
        method: {"hits": 0, "rr_sum": 0.0, "ranks": []}
        for method in methods
    }
    latencies = {f"{method}_ms": [] for method in methods}

    for question in questions:
        tenant = question["tenant_id"]
        query = question["query"]
        expected = question["expected_doc_id"]

        vector_hits, elapsed = timed(
            lambda: retriever.vector.search(tenant, query, k)
        )
        latencies["vector_ms"].append(elapsed)

        graph_hits, elapsed = timed(
            lambda: retriever.graph.search(tenant, query, k)
        )
        latencies["graph_ms"].append(elapsed)

        hybrid_hits, elapsed = timed(
            lambda: retriever.search(tenant, query, k)[0]
        )
        latencies["hybrid_ms"].append(elapsed)

        for method, hits in (
            ("vector", vector_hits),
            ("graph", graph_hits),
            ("hybrid", hybrid_hits),
        ):
            rr = reciprocal_rank(hits, expected)
            metrics[method]["rr_sum"] += rr
            metrics[method]["hits"] += int(rr > 0)
            metrics[method]["ranks"].append(
                next(
                    (
                        rank
                        for rank, hit in enumerate(hits, start=1)
                        if hit.doc_id == expected
                    ),
                    None,
                )
            )

    denominator = max(len(questions), 1)
    for method in methods:
        metrics[method]["recall_at_k"] = metrics[method]["hits"] / denominator
        metrics[method]["mrr"] = metrics[method]["rr_sum"] / denominator
        metrics[method]["mean_rank"] = (
            sum(rank for rank in metrics[method]["ranks"] if rank is not None)
            / denominator
        )

    latency_report = {
        name: {
            "p50_ms": percentile(values, 0.50),
            "p95_ms": percentile(values, 0.95),
            "max_ms": max(values, default=0.0),
        }
        for name, values in latencies.items()
    }
    return metrics, latency_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run reproducible experiments over the checked-in GraphRAG fixture."
    )
    parser.add_argument("--corpus", default="enterprise_data/corpus.jsonl")
    parser.add_argument("--questions", default="enterprise_data/eval_questions.json")
    parser.add_argument("--output", default="enterprise_data/fixture_experiments.json")
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    questions_path = Path(args.questions)
    corpus = load_corpus(corpus_path)
    questions = load_questions(questions_path)
    documents = [item for items in corpus.values() for item in items]

    token_lengths = [
        len(item["text"].split())
        for item in documents
    ]
    character_lengths = [
        len(item["text"])
        for item in documents
    ]
    tenant_counts = {
        tenant: len(items)
        for tenant, items in sorted(corpus.items())
    }

    root = Path(tempfile.mkdtemp(prefix="enterprise-graphrag-experiments-"))
    vector = TenantFAISS(str(root / "faiss"), HashEmbedder(128))
    graph = TenantMemoryGraph()
    security = SecurityGateway(threshold=80, marker_threshold=2)
    retriever = HybridRetriever(
        vector=vector,
        graph=graph,
        security=security,
        vector_weight=0.55,
        graph_weight=0.45,
        rrf_k=60,
    )

    for tenant, items in corpus.items():
        retriever.add(tenant, items)

    retrieval_by_k = {}
    for k in range(1, min(5, len(documents)) + 1):
        metrics, latencies = evaluate_retrieval(retriever, questions, k)
        retrieval_by_k[str(k)] = {
            "metrics": metrics,
            "latency_ms": latencies,
        }

    weight_sweep = []
    for step in range(11):
        vector_weight = step / 10
        graph_weight = 1.0 - vector_weight
        hybrid_metrics = []
        for question in questions:
            tenant = question["tenant_id"]
            query = question["query"]
            expected = question["expected_doc_id"]
            vector_hits = retriever.vector.search(tenant, query, 5)
            graph_hits = retriever.graph.search(tenant, query, 5)
            from enterprise_graphrag.fusion import weighted_rrf
            hybrid_hits = weighted_rrf(
                {"vector": vector_hits, "graph": graph_hits},
                {"vector": vector_weight, "graph": graph_weight},
                k=60,
                limit=5,
            )
            hybrid_metrics.append(reciprocal_rank(hybrid_hits, expected))
        weight_sweep.append(
            {
                "vector_weight": round(vector_weight, 2),
                "graph_weight": round(graph_weight, 2),
                "recall_at_5": sum(value > 0 for value in hybrid_metrics) / len(hybrid_metrics),
                "mrr": sum(hybrid_metrics) / len(hybrid_metrics),
            }
        )

    injection = retriever.search("acme", "imported memo", 5)
    allowed, blocked, vector_count, graph_count = injection
    blocked_docs = [item["doc_id"] for item in blocked]

    cross_tenant = []
    for question in questions:
        allowed_hits = retriever.search(
            question["tenant_id"],
            question["query"],
            5,
        )[0]
        leaks = [
            hit.doc_id
            for hit in allowed_hits
            if hit.tenant_id != question["tenant_id"]
        ]
        cross_tenant.append(
            {
                "tenant": question["tenant_id"],
                "query": question["query"],
                "leaks": leaks,
            }
        )

    security_marker_counts = {}
    for item in documents:
        decision = security.inspect(
            item["title"] + "\n" + item["text"],
            direct=False,
        )
        security_marker_counts[item["doc_id"]] = {
            "allowed": decision["allowed"],
            "marker_count": decision["marker_count"],
        }

    report = {
        "dataset": {
            "corpus_path": str(corpus_path),
            "questions_path": str(questions_path),
            "documents": len(documents),
            "tenants": len(corpus),
            "documents_per_tenant": tenant_counts,
            "injection_documents": sum(item["doc_id"].endswith("injected") for item in documents),
            "text_characters": {
                "min": min(character_lengths, default=0),
                "mean": statistics.mean(character_lengths) if character_lengths else 0.0,
                "max": max(character_lengths, default=0),
            },
            "text_tokens": {
                "min": min(token_lengths, default=0),
                "mean": statistics.mean(token_lengths) if token_lengths else 0.0,
                "max": max(token_lengths, default=0),
            },
        },
        "retrieval_by_k": retrieval_by_k,
        "weight_sweep": weight_sweep,
        "security_case": {
            "query": "imported memo",
            "vector_candidates": vector_count,
            "graph_candidates": graph_count,
            "blocked_document_ids": blocked_docs,
            "all_blocked_contexts_are_nonempty": all(bool(item) for item in blocked),
            "injection_reached_allowed_results": any(
                hit.doc_id == "acme-injected" for hit in allowed
            ),
        },
        "tenant_isolation": {
            "cases": cross_tenant,
            "total_leaks": sum(len(case["leaks"]) for case in cross_tenant),
        },
        "security_markers": security_marker_counts,
    }

    report["passed"] = (
        report["dataset"]["documents"] == 5
        and report["dataset"]["tenants"] == 2
        and report["security_case"]["blocked_document_ids"] == ["acme-injected"]
        and not report["security_case"]["injection_reached_allowed_results"]
        and report["tenant_isolation"]["total_leaks"] == 0
        and all(
            retrieval_by_k[str(k)]["metrics"]["hybrid"]["recall_at_k"] == 1.0
            for k in range(1, min(5, len(documents)) + 1)
        )
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    import statistics
    main()
