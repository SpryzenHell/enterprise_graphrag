from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import statistics
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import torch
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

from enterprise_graphrag.fusion import weighted_rrf
from enterprise_graphrag.neo4j_store import Neo4jTenantStore
from enterprise_graphrag.vector_faiss import TenantFAISS

MODEL_ID = "BAAI/bge-base-en-v1.5"
MODEL_LICENSE = "MIT"
DATASET_ID = "hotpot_qa"
DATASET_CONFIG = "distractor"
DATASET_LICENSE = "CC-BY-SA-4.0"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


class BGEEmbedder:
    """Adapter for the repository FAISS index; prefixes queries but not passages."""

    def __init__(self, model: SentenceTransformer):
        self.model = model
        self.dimension = int(model.get_sentence_embedding_dimension())

    def embed(self, texts: list[str]) -> list[list[float]]:
        prepared = [
            text if "\n" in text else QUERY_PREFIX + text
            for text in texts
        ]
        vectors = self.model.encode(
            prepared,
            batch_size=int(os.getenv("GRAGRAPH_EMBED_BATCH_SIZE", "128")),
            convert_to_numpy=True,
            normalize_embeddings=False,
            show_progress_bar=False,
        )
        return vectors.tolist()


def normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def short_id(value: str) -> str:
    return hashlib.sha256(normalize_title(value).encode("utf-8")).hexdigest()[:24]


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(float(value) for value in values)
    index = max(0, min(len(values) - 1, int((len(values) - 1) * p + 0.999999)))
    return round(values[index], 4)


def latency_summary(values: list[float]) -> dict:
    return {
        "n": len(values),
        "p50_ms": percentile(values, 0.50),
        "p95_ms": percentile(values, 0.95),
        "max_ms": round(max(values), 4) if values else None,
        "mean_ms": round(statistics.mean(values), 4) if values else None,
    }


def doc_text(title: str, sentences: list[str]) -> str:
    body = " ".join(str(sentence).strip() for sentence in sentences if str(sentence).strip())
    return body or str(title)


def load_hotpotqa(cache_dir: Path, max_queries: int, seed: int):
    cache_dir.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(
        DATASET_ID,
        DATASET_CONFIG,
        split="validation",
        cache_dir=str(cache_dir),
    )
    eligible = []
    for row in dataset:
        try:
            question = str(row["question"]).strip()
            answer = str(row.get("answer") or "").strip()
            facts = row["supporting_facts"]
            context = row["context"]
            titles = [str(x).strip() for x in facts["title"] if str(x).strip()]
            if not question or not titles or not isinstance(context, dict):
                continue
            eligible.append({
                "query_id": str(row.get("_id") or row.get("id") or short_id(question)),
                "question": question,
                "answer": answer,
                "supporting_titles": sorted({normalize_title(x) for x in titles}),
                "context": context,
                "type": str(row.get("type") or "unknown"),
                "level": str(row.get("level") or "unknown"),
            })
        except (KeyError, TypeError):
            continue
    if not eligible:
        raise RuntimeError("HotpotQA validation contained no usable question/context/supporting-fact rows")
    if max_queries > 0 and len(eligible) > max_queries:
        eligible = random.Random(seed).sample(eligible, max_queries)
    return dataset, eligible


def build_corpus(queries: list[dict]) -> list[dict]:
    documents: dict[str, dict] = {}
    for query in queries:
        context = query["context"]
        titles = context.get("title", [])
        sentence_lists = context.get("sentences", [])
        for title, sentences in zip(titles, sentence_lists):
            title = str(title).strip()
            if not title:
                continue
            content = doc_text(title, list(sentences) if isinstance(sentences, (list, tuple)) else [str(sentences)])
            key = normalize_title(title)
            if key not in documents:
                documents[key] = {
                    "doc_id": "hotpot-" + short_id(title),
                    "title": title,
                    "text": content,
                }
            else:
                old = documents[key]["text"]
                if normalize_title(content) not in normalize_title(old):
                    documents[key]["text"] = old + "\n" + content
    return list(documents.values())


def ranking_metrics(query_rows: list[dict], rankings: dict[str, list[str]]) -> dict:
    per_query_recall = []
    per_query_hit = []
    per_query_all = []
    per_query_rr = []
    per_query_ndcg = []
    per_query_precision = []
    per_query_answer_text = []
    for row in query_rows:
        query_id = row["query_id"]
        gold_titles = set(row["supporting_titles"])
        ranked_titles = [
            normalize_title(value)
            for value in rankings.get(query_id, [])[:10]
        ]
        ranked_set = set(ranked_titles)
        found = gold_titles & ranked_set
        per_query_recall.append(len(found) / max(len(gold_titles), 1))
        per_query_hit.append(float(bool(found)))
        per_query_all.append(float(bool(gold_titles) and gold_titles.issubset(ranked_set)))
        first_rank = next(
            (rank for rank, title in enumerate(ranked_titles, start=1) if title in gold_titles),
            None,
        )
        per_query_rr.append(1.0 / first_rank if first_rank is not None else 0.0)
        gains = [1 if title in gold_titles else 0 for title in ranked_titles]
        dcg = sum(gain / __import__("math").log2(rank + 1) for rank, gain in enumerate(gains, start=1))
        ideal = sum(1.0 / __import__("math").log2(rank + 1) for rank in range(1, min(len(gold_titles), 10) + 1))
        per_query_ndcg.append(dcg / ideal if ideal else 0.0)
        per_query_precision.append(len(found) / 10.0)

        answer = normalize_title(row.get("answer", ""))
        if len(answer) < 2 or answer in {"yes", "no"}:
            per_query_answer_text.append(float(answer in {"yes", "no"} and any(answer in normalize_title(title) for title in ranked_titles)))
        else:
            per_query_answer_text.append(float(any(answer in normalize_title(text) for text in rankings.get(query_id + "::answer_text", []))))
    n = len(per_query_recall)
    if not n:
        return {"n_queries": 0}
    return {
        "n_queries": n,
        "supporting_title_recall@10": round(statistics.mean(per_query_recall), 6),
        "hit@10": round(statistics.mean(per_query_hit), 6),
        "all_supporting_titles@10": round(statistics.mean(per_query_all), 6),
        "mrr@10": round(statistics.mean(per_query_rr), 6),
        "ndcg@10": round(statistics.mean(per_query_ndcg), 6),
        "supporting_title_precision@10": round(statistics.mean(per_query_precision), 6),
        "answer_text_present_in_top10": round(statistics.mean(per_query_answer_text), 6),
    }


def evaluate_rankings(queries: list[dict], candidate_lists: dict[str, dict[str, list]], qid_to_title: dict[str, dict[str, str]]) -> dict:
    controls = {}
    for backend in ("vector", "neo4j"):
        controls[backend] = {}
        for qid, hits in candidate_lists[backend].items():
            controls[backend][qid] = [hit.title for hit in hits[:10]]
            controls[backend][qid + "::answer_text"] = [hit.text for hit in hits[:10]]
    results = {
        backend: ranking_metrics(queries, controls[backend])
        for backend in ("vector", "neo4j")
    }
    shuffled = list(queries)
    random.Random(20261015).shuffle(shuffled)
    midpoint = max(1, len(shuffled) // 2)
    calibration = shuffled[:midpoint]
    heldout = shuffled[midpoint:] or calibration
    calibration_qids = {row["query_id"] for row in calibration}
    heldout_qids = {row["query_id"] for row in heldout}
    weights = (0.0, 0.10, 0.20, 0.30, 0.45, 0.60, 0.75, 0.90, 1.0)
    depths = (10, 20, 50, 100)
    sweep = []
    for depth in depths:
        for vector_weight in weights:
            ranked: dict[str, list[str]] = {}
            answer_texts: dict[str, list[str]] = {}
            for qid in candidate_lists["vector"]:
                fused = weighted_rrf(
                    {
                        "vector": candidate_lists["vector"][qid][:depth],
                        "graph": candidate_lists["neo4j"][qid][:depth],
                    },
                    {"vector": vector_weight, "graph": 1.0 - vector_weight},
                    k=60,
                    limit=10,
                )
                ranked[qid] = [hit.title for hit in fused]
                answer_texts[qid + "::answer_text"] = [hit.text for hit in fused]
            full_rankings = dict(ranked)
            full_rankings.update(answer_texts)
            calibration_metrics = ranking_metrics(calibration, full_rankings)
            heldout_metrics = ranking_metrics(heldout, full_rankings)
            sweep.append({
                "candidate_depth": depth,
                "vector_weight": vector_weight,
                "graph_weight": round(1.0 - vector_weight, 2),
                "vector_only_control": vector_weight == 1.0,
                "graph_only_control": vector_weight == 0.0,
                "calibration": calibration_metrics,
                "heldout": heldout_metrics,
            })
    hybrid = [row for row in sweep if 0.0 < row["vector_weight"] < 1.0]
    best = max(
        hybrid,
        key=lambda row: (
            row["calibration"]["supporting_title_recall@10"],
            row["calibration"]["all_supporting_titles@10"],
            row["calibration"]["mrr@10"],
            row["vector_weight"],
            -row["candidate_depth"],
        ),
    )
    best_heldout = ranking_metrics(heldout, {
        **{qid: [hit.title for hit in weighted_rrf(
            {
                "vector": candidate_lists["vector"][qid][:best["candidate_depth"]],
                "graph": candidate_lists["neo4j"][qid][:best["candidate_depth"]],
            },
            {"vector": best["vector_weight"], "graph": 1.0 - best["vector_weight"]},
            k=60, limit=10,
        )] for qid in candidate_lists["vector"]},
        **{qid + "::answer_text": [hit.text for hit in weighted_rrf(
            {
                "vector": candidate_lists["vector"][qid][:best["candidate_depth"]],
                "graph": candidate_lists["neo4j"][qid][:best["candidate_depth"]],
            },
            {"vector": best["vector_weight"], "graph": 1.0 - best["vector_weight"]},
            k=60, limit=10,
        )] for qid in candidate_lists["vector"]},
    })
    selected_sweep = {
        "selection_rule": "Maximize calibration supporting-title recall@10, then all-supporting-titles@10, then MRR@10; ties prefer more vector weight and the shallower candidate pool.",
        "seed": 20261015,
        "calibration_queries": len(calibration),
        "heldout_queries": len(heldout),
        "selected": best,
        "selected_heldout": best_heldout,
        "all_configurations": sweep,
        "warning": "HotpotQA validation questions are split into calibration and held-out subsets after selecting a deterministic query sample; the held-out subset is not the hidden test set.",
    }
    return {"controls": results, "rrf_tuning": selected_sweep}


def main():
    parser = argparse.ArgumentParser(description="Measure BGE, Neo4j entity traversal and RRF on HotpotQA multi-hop retrieval.")
    parser.add_argument("--output-dir", default="artifacts/hotpotqa-multihop")
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "hotpotqa-multihop"))
    parser.add_argument("--max-queries", type=int, default=400)
    parser.add_argument("--seed", type=int, default=20261015)
    parser.add_argument("--embedding-batch-size", type=int, default=128)
    args = parser.parse_args()

    os.environ["GRAGRAPH_EMBED_BATCH_SIZE"] = str(args.embedding_batch_size)
    output_dir = Path(args.output_dir)
    cache_dir = Path(args.cache_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    start_utc = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    raw_dataset, queries = load_hotpotqa(cache_dir, args.max_queries, args.seed)
    corpus = build_corpus(queries)
    if not corpus:
        raise RuntimeError("HotpotQA sample produced an empty passage corpus")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(MODEL_ID, device=device)
    embedder = BGEEmbedder(model)

    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "")
    neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
    if not neo4j_password:
        raise RuntimeError("NEO4J_PASSWORD must be set for the multi-hop benchmark")

    with tempfile.TemporaryDirectory(prefix="hotpotqa-faiss-") as tmp:
        vector = TenantFAISS(str(Path(tmp) / "faiss"), embedder)
        index_started = time.perf_counter()
        vector.add("hotpotqa", corpus)
        vector_index_seconds = time.perf_counter() - index_started
        store = Neo4jTenantStore(neo4j_uri, neo4j_user, neo4j_password, neo4j_database)
        try:
            for _ in range(30):
                try:
                    store.verify()
                    break
                except Exception:
                    time.sleep(1)
            else:
                raise RuntimeError("Neo4j did not become ready within 30 seconds")
            store.ensure_schema()
            neo_index_started = time.perf_counter()
            store.add_many("hotpotqa", corpus)
            neo_index_seconds = time.perf_counter() - neo_index_started
            candidate_depth = 100
            warm_query = queries[0]["question"]
            vector.search("hotpotqa", warm_query, candidate_depth)
            store.search("hotpotqa", warm_query, candidate_depth)

            candidate_lists = {"vector": {}, "neo4j": {}}
            latencies = {"vector_top100_ms": [], "neo4j_top100_ms": []}
            for row in queries:
                qid = row["query_id"]
                query = row["question"]
                tick = time.perf_counter()
                vector_hits = vector.search("hotpotqa", query, candidate_depth)
                latencies["vector_top100_ms"].append((time.perf_counter() - tick) * 1000)
                tick = time.perf_counter()
                graph_hits = store.search("hotpotqa", query, candidate_depth)
                latencies["neo4j_top100_ms"].append((time.perf_counter() - tick) * 1000)
                candidate_lists["vector"][qid] = vector_hits
                candidate_lists["neo4j"][qid] = graph_hits

            controls = {}
            for backend in ("vector", "neo4j"):
                title_and_text = {}
                for row in queries:
                    qid = row["query_id"]
                    hits = candidate_lists[backend][qid][:10]
                    title_and_text[qid] = [hit.title for hit in hits]
                    title_and_text[qid + "::answer_text"] = [hit.text for hit in hits]
                controls[backend] = ranking_metrics(queries, title_and_text)

            sweep = evaluate_rankings(queries, candidate_lists, {})
            result = {
                "schema_version": 1,
                "started_utc": start_utc,
                "completed_utc": datetime.now(timezone.utc).isoformat(),
                "elapsed_seconds": round(time.perf_counter() - started, 3),
                "seed": args.seed,
                "dataset": f"{DATASET_ID}/{DATASET_CONFIG} validation",
                "dataset_license": DATASET_LICENSE,
                "dataset_reference": "https://hotpotqa.github.io/",
                "embedding_model": MODEL_ID,
                "embedding_model_license": MODEL_LICENSE,
                "device": device,
                "raw_validation_rows": len(raw_dataset),
                "evaluated_queries": len(queries),
                "deduplicated_corpus_documents": len(corpus),
                "vector_index_build_seconds": round(vector_index_seconds, 3),
                "neo4j_index_build_seconds": round(neo_index_seconds, 3),
                "query_latency": {
                    key: latency_summary(value)
                    for key, value in latencies.items()
                },
                "controls": controls,
                "rrf_tuning": sweep["rrf_tuning"],
                "limitations": [
                    "The benchmark indexes only passages present in the sampled HotpotQA distractor contexts, not all Wikipedia.",
                    "Entity extraction is deterministic title/body capitalization matching; this tests the current production retriever rather than an idealized knowledge graph.",
                    "The held-out half is a seeded validation subset, not the official hidden test split.",
                    "Support-title retrieval is evidence-retrieval quality, not a complete end-to-end answer hallucination evaluation.",
                ],
            }
        finally:
            store.close()

    result["completed_utc"] = datetime.now(timezone.utc).isoformat()
    result["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    (output_dir / "hotpotqa_multihop_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    selected = result["rrf_tuning"]["selected"]
    heldout = result["rrf_tuning"]["selected_heldout"]
    vector = result["controls"]["vector"]
    graph = result["controls"]["neo4j"]
    lines = [
        "# HotpotQA multi-hop retrieval: vector vs. Neo4j vs. weighted RRF",
        "",
        f"- Started UTC: {result['started_utc']}",
        f"- Completed UTC: {result['completed_utc']}",
        f"- Elapsed seconds: {result['elapsed_seconds']}",
        f"- Dataset: {result['dataset']} ({result['dataset_license']})",
        f"- Embedding: {MODEL_ID} ({MODEL_LICENSE}), device={device}",
        f"- Queries: {len(queries)}; deduplicated passages: {len(corpus)}",
        f"- Vector index build: {result['vector_index_build_seconds']} seconds; Neo4j bulk ingest: {result['neo4j_index_build_seconds']} seconds",
        "",
        "| Method | Support recall@10 | Hit@10 | All supporting titles@10 | MRR@10 | nDCG@10 | Answer string present@10 |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Vector-only | {vector['supporting_title_recall@10']:.4f} | {vector['hit@10']:.4f} | {vector['all_supporting_titles@10']:.4f} | {vector['mrr@10']:.4f} | {vector['ndcg@10']:.4f} | {vector['answer_text_present_in_top10']:.4f} |",
        f"| Neo4j graph-only | {graph['supporting_title_recall@10']:.4f} | {graph['hit@10']:.4f} | {graph['all_supporting_titles@10']:.4f} | {graph['mrr@10']:.4f} | {graph['ndcg@10']:.4f} | {graph['answer_text_present_in_top10']:.4f} |",
        f"| RRF selected on calibration | {heldout['supporting_title_recall@10']:.4f} | {heldout['hit@10']:.4f} | {heldout['all_supporting_titles@10']:.4f} | {heldout['mrr@10']:.4f} | {heldout['ndcg@10']:.4f} | {heldout['answer_text_present_in_top10']:.4f} |",
        "",
        f"- Selected calibration weight: vector={selected['vector_weight']:.2f}, graph={selected['graph_weight']:.2f}; candidate depth={selected['candidate_depth']}.",
        f"- Held-out queries: {result['rrf_tuning']['heldout_queries']}; calibration queries: {result['rrf_tuning']['calibration_queries']}.",
        "",
        "## Query latency (after model/index warm-up)",
        "",
        "| Retriever | P50 ms | P95 ms | Max ms |",
        "|---|---:|---:|---:|",
    ]
    for name, summary in result["query_latency"].items():
        lines.append(f"| {name} | {summary['p50_ms']} | {summary['p95_ms']} | {summary['max_ms']} |")
    lines += [
        "",
        "## Interpretation limits",
        "",
        *[f"- {line}" for line in result["limitations"]],
        "",
        "Only aggregate retrieval metrics are saved; question text, answers, and passages are not copied into the report.",
    ]
    (output_dir / "hotpotqa_multihop_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
