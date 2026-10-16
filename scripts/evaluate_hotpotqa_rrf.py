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
    answer_text_eval_count = 0
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
        # Exact answer-string coverage is meaningful for non-binary answers only;
        # "yes"/"no" would otherwise create a spurious substring hit.
        if len(answer) >= 2 and answer not in {"yes", "no"}:
            answer_text_eval_count += 1
            per_query_answer_text.append(
                float(any(answer in normalize_title(text) for text in rankings.get(query_id + "::answer_text", [])))
            )
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
        "answer_text_present_in_top10": round(statistics.mean(per_query_answer_text), 6) if per_query_answer_text else None,
        "answer_text_evaluated_queries": answer_text_eval_count,
    }



def candidate_pool_metrics(
    queries: list[dict],
    candidate_lists: dict[str, dict[str, list]],
    depth: int = 100,
) -> dict:
    """Measure evidence coverage before top-10 ranking and RRF.

    This separates candidate-generation failures from ordering failures. It also
    counts supporting titles the graph pool contributes that are absent from the
    vector pool at the same depth.
    """
    gold_by_qid = {
        row["query_id"]: {normalize_title(title) for title in row["supporting_titles"]}
        for row in queries
    }
    vector_candidates = candidate_lists.get("vector", {})
    vector_support_at_depth = {}
    for row in queries:
        qid = row["query_id"]
        vector_support_at_depth[qid] = {
            normalize_title(hit.title)
            for hit in vector_candidates.get(qid, [])[:depth]
        } & gold_by_qid[qid]

    result = {}
    for backend, per_query in candidate_lists.items():
        per_query_recall = []
        per_query_hit = []
        candidate_counts = []
        added_support_docs = 0
        queries_with_added_support = 0
        for row in queries:
            qid = row["query_id"]
            gold = gold_by_qid[qid]
            hits = per_query.get(qid, [])[:depth]
            ranked = {normalize_title(hit.title) for hit in hits}
            found = ranked & gold
            per_query_recall.append(len(found) / max(len(gold), 1))
            per_query_hit.append(float(bool(found)))
            candidate_counts.append(len(hits))
            if backend not in ("vector",):
                added = found - vector_support_at_depth.get(qid, set())
                added_support_docs += len(added)
                queries_with_added_support += int(bool(added))
        result[backend] = {
            "candidate_depth": depth,
            "n_queries": len(queries),
            "mean_candidate_count": round(statistics.mean(candidate_counts), 3) if candidate_counts else 0.0,
            "supporting_title_recall_in_pool": round(statistics.mean(per_query_recall), 6) if per_query_recall else 0.0,
            "queries_with_any_support_in_pool": round(statistics.mean(per_query_hit), 6) if per_query_hit else 0.0,
            "supporting_titles_added_vs_vector_pool": added_support_docs,
            "queries_with_added_support_vs_vector_pool": queries_with_added_support,
        }
    return result

def evaluate_rankings(
    queries: list[dict],
    candidate_lists: dict[str, dict[str, list]],
    qid_to_title: dict[str, dict[str, str]] | None = None,
) -> dict:
    """Compare direct graph search with vector-seeded graph expansion on held-out questions."""
    def rankings_for_hits(backend: str) -> dict:
        rankings = {}
        for qid, hits in candidate_lists[backend].items():
            rankings[qid] = [hit.title for hit in hits[:10]]
            rankings[qid + "::answer_text"] = [hit.text for hit in hits[:10]]
        return rankings

    profiles = ["neo4j", "neo4j_vector_seeded"]
    if "neo4j_vector_seeded" in candidate_lists:
        enriched = {}
        for qid in candidate_lists["vector"]:
            enriched[qid] = weighted_rrf(
                {
                    "graph_fulltext": candidate_lists["neo4j"].get(qid, []),
                    "graph_vector_seeded_two_hop": candidate_lists["neo4j_vector_seeded"].get(qid, []),
                },
                {"graph_fulltext": 0.20, "graph_vector_seeded_two_hop": 0.80},
                k=60,
                limit=100,
            )
        candidate_lists["neo4j_enriched"] = enriched
        profiles.append("neo4j_enriched")

    controls = {
        "vector": ranking_metrics(queries, rankings_for_hits("vector")),
        "neo4j": ranking_metrics(queries, rankings_for_hits("neo4j")),
    }
    if "neo4j_vector_seeded" in candidate_lists:
        controls["neo4j_vector_seeded"] = ranking_metrics(
            queries, rankings_for_hits("neo4j_vector_seeded")
        )
        controls["neo4j_enriched"] = ranking_metrics(
            queries, rankings_for_hits("neo4j_enriched")
        )

    shuffled = list(queries)
    random.Random(20261015).shuffle(shuffled)
    midpoint = max(1, len(shuffled) // 2)
    calibration = shuffled[:midpoint]
    heldout = shuffled[midpoint:] or calibration
    weights = (0.0, 0.10, 0.20, 0.30, 0.45, 0.60, 0.75, 0.90, 0.95, 0.99, 1.0)
    vector_depths = (5, 10, 20, 100)
    graph_depths = (10, 50, 100)
    sweep = []

    for profile in profiles:
        for vector_depth in vector_depths:
            for graph_depth in graph_depths:
                for vector_weight in weights:
                    ranked: dict[str, list[str]] = {}
                    answer_texts: dict[str, list[str]] = {}
                    for qid in candidate_lists["vector"]:
                        fused = weighted_rrf(
                            {
                                "vector": candidate_lists["vector"][qid][:vector_depth],
                                "graph": candidate_lists[profile].get(qid, [])[:graph_depth],
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
                        "candidate_profile": profile,
                        "vector_candidate_depth": vector_depth,
                        "graph_candidate_depth": graph_depth,
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
            row["calibration"]["ndcg@10"],
            row["vector_weight"],
            -row["vector_candidate_depth"],
            -row["graph_candidate_depth"],
            row["candidate_profile"] == "neo4j_vector_seeded",
        ),
    )

    def fuse_config(
        profile: str,
        vector_depth: int,
        graph_depth: int,
        vector_weight: float,
        qids: list[str],
    ) -> dict:
        ranked: dict[str, list[str]] = {}
        answer_texts: dict[str, list[str]] = {}
        for qid in qids:
            fused = weighted_rrf(
                {
                    "vector": candidate_lists["vector"][qid][:vector_depth],
                    "graph": candidate_lists[profile].get(qid, [])[:graph_depth],
                },
                {"vector": vector_weight, "graph": 1.0 - vector_weight},
                k=60,
                limit=10,
            )
            ranked[qid] = [hit.title for hit in fused]
            answer_texts[qid + "::answer_text"] = [hit.text for hit in fused]
        ranked.update(answer_texts)
        return ranked

    best_heldout = ranking_metrics(
        heldout,
        fuse_config(
            best["candidate_profile"],
            best["vector_candidate_depth"],
            best["graph_candidate_depth"],
            best["vector_weight"],
            list(candidate_lists["vector"]),
        ),
    )
    vector_heldout = ranking_metrics(
        heldout,
        fuse_config("neo4j", 100, 100, 1.0, list(candidate_lists["vector"])),
    )
    recall_delta = round(
        best_heldout["supporting_title_recall@10"] - vector_heldout["supporting_title_recall@10"], 6
    )
    mrr_delta = round(best_heldout["mrr@10"] - vector_heldout["mrr@10"], 6)
    ndcg_delta = round(best_heldout["ndcg@10"] - vector_heldout["ndcg@10"], 6)
    answer_delta = round(
        (best_heldout.get("answer_text_present_in_top10") or 0.0)
        - (vector_heldout.get("answer_text_present_in_top10") or 0.0),
        6,
    )
    acceptance = {
        "criteria": {
            "minimum_supporting_title_recall_gain": 0.01,
            "maximum_mrr_regression": 0.02,
            "maximum_ndcg_regression": 0.02,
        },
        "supporting_title_recall_gain": recall_delta,
        "mrr_delta": mrr_delta,
        "ndcg_delta": ndcg_delta,
        "answer_text_presence_delta": answer_delta,
        "support_recall_improved": recall_delta >= 0.01,
        "mrr_not_materially_worse": mrr_delta >= -0.02,
        "ndcg_not_materially_worse": ndcg_delta >= -0.02,
    }
    acceptance["candidate_clears_retrieval_gate"] = all((
        acceptance["support_recall_improved"],
        acceptance["mrr_not_materially_worse"],
        acceptance["ndcg_not_materially_worse"],
    ))
    selected_sweep = {
        "selection_rule": "Maximize calibration supporting-title recall@10, then all-supporting-titles@10, MRR@10 and nDCG@10; ties prefer more vector weight, shallower vector pool, shallower graph pool, then the vector-seeded graph profile over the weaker direct-graph blend.",
        "seed": 20261015,
        "calibration_queries": len(calibration),
        "heldout_queries": len(heldout),
        "selected": best,
        "selected_heldout": best_heldout,
        "vector_only_heldout": vector_heldout,
        "acceptance": acceptance,
        "all_configurations": sweep,
        "warning": "HotpotQA validation questions are split into calibration and held-out subsets after selecting a deterministic query sample; the held-out subset is not the hidden test set.",
    }
    return {"controls": controls, "rrf_tuning": selected_sweep}


def main():
    parser = argparse.ArgumentParser(description="Measure BGE, Neo4j entity traversal and RRF on HotpotQA multi-hop retrieval.")
    parser.add_argument("--output-dir", default="artifacts/hotpotqa-multihop")
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "hotpotqa-multihop"))
    parser.add_argument("--max-queries", type=int, default=400)
    parser.add_argument("--seed", type=int, default=20261015)
    parser.add_argument("--embedding-batch-size", type=int, default=128)
    parser.add_argument("--anchor-depth", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.anchor_depth <= 100:
        parser.error("--anchor-depth must be between 1 and 100")

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

            candidate_lists = {"vector": {}, "neo4j": {}, "neo4j_vector_seeded": {}}
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
                tick = time.perf_counter()
                seeded_graph_hits = store.expand_from_anchors(
                    "hotpotqa",
                    [hit.doc_id for hit in vector_hits[:args.anchor_depth]],
                    candidate_depth,
                )
                latencies.setdefault("neo4j_vector_seeded_top100_ms", []).append((time.perf_counter() - tick) * 1000)
                candidate_lists["vector"][qid] = vector_hits
                candidate_lists["neo4j"][qid] = graph_hits
                candidate_lists["neo4j_vector_seeded"][qid] = seeded_graph_hits

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
            # Preserve all four retrieval controls. Previously this script computed
            # seeded and enriched graph metrics in evaluate_rankings(), but discarded
            # them from the final JSON and printed a zero-valued fallback in Markdown.
            controls.update(sweep["controls"])
            candidate_coverage = candidate_pool_metrics(
                queries,
                candidate_lists,
                depth=candidate_depth,
            )
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
                "vector_anchor_depth_for_graph_expansion": args.anchor_depth,
                "vector_index_build_seconds": round(vector_index_seconds, 3),
                "neo4j_index_build_seconds": round(neo_index_seconds, 3),
                "query_latency": {
                    key: latency_summary(value)
                    for key, value in latencies.items()
                },
                "controls": controls,
                "candidate_pool_coverage": candidate_coverage,
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
    seeded_graph = result["controls"].get("neo4j_vector_seeded", {"supporting_title_recall@10": 0, "hit@10": 0, "all_supporting_titles@10": 0, "mrr@10": 0, "ndcg@10": 0, "answer_text_present_in_top10": 0})
    enriched_graph = result["controls"].get("neo4j_enriched", {"supporting_title_recall@10": 0, "hit@10": 0, "all_supporting_titles@10": 0, "mrr@10": 0, "ndcg@10": 0, "answer_text_present_in_top10": 0})
    acceptance = result["rrf_tuning"]["acceptance"]
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
        f"- Vector anchors passed to each Neo4j expansion: {result['vector_anchor_depth_for_graph_expansion']}",
        "",
        "## Candidate generation coverage before top-10 ranking",
        "",
        "| Candidate pool | Mean candidates | Support recall in top-100 pool | Queries with any support | Supporting titles added vs vector top-100 | Queries with added support |",
        "|---|---:|---:|---:|---:|---:|",
        *[
            f"| {name} | {summary['mean_candidate_count']:.1f} | {summary['supporting_title_recall_in_pool']:.4f} | {summary['queries_with_any_support_in_pool']:.4f} | {summary['supporting_titles_added_vs_vector_pool']} | {summary['queries_with_added_support_vs_vector_pool']} |"
            for name, summary in result["candidate_pool_coverage"].items()
        ],
        "",
        "These metrics measure whether graph traversal generates relevant candidates at all, independent of the top-10 ordering and RRF.",
        "",
        "",
        "| Method | Support recall@10 | Hit@10 | All supporting titles@10 | MRR@10 | nDCG@10 | Answer string present@10 |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Vector-only | {vector['supporting_title_recall@10']:.4f} | {vector['hit@10']:.4f} | {vector['all_supporting_titles@10']:.4f} | {vector['mrr@10']:.4f} | {vector['ndcg@10']:.4f} | {vector['answer_text_present_in_top10']:.4f} |",
        f"| Neo4j direct graph-only | {graph['supporting_title_recall@10']:.4f} | {graph['hit@10']:.4f} | {graph['all_supporting_titles@10']:.4f} | {graph['mrr@10']:.4f} | {graph['ndcg@10']:.4f} | {graph['answer_text_present_in_top10']:.4f} |",
        f"| Vector-seeded two-hop graph-only | {seeded_graph['supporting_title_recall@10']:.4f} | {seeded_graph['hit@10']:.4f} | {seeded_graph['all_supporting_titles@10']:.4f} | {seeded_graph['mrr@10']:.4f} | {seeded_graph['ndcg@10']:.4f} | {seeded_graph['answer_text_present_in_top10']:.4f} |",
        f"| Direct + vector-seeded graph-only | {enriched_graph['supporting_title_recall@10']:.4f} | {enriched_graph['hit@10']:.4f} | {enriched_graph['all_supporting_titles@10']:.4f} | {enriched_graph['mrr@10']:.4f} | {enriched_graph['ndcg@10']:.4f} | {enriched_graph['answer_text_present_in_top10']:.4f} |",
        f"| RRF selected on calibration | {heldout['supporting_title_recall@10']:.4f} | {heldout['hit@10']:.4f} | {heldout['all_supporting_titles@10']:.4f} | {heldout['mrr@10']:.4f} | {heldout['ndcg@10']:.4f} | {heldout['answer_text_present_in_top10']:.4f} |",
        "",
        f"- Selected graph profile: {selected['candidate_profile']}; calibration weight: vector={selected['vector_weight']:.2f}, graph={selected['graph_weight']:.2f}; vector candidate depth={selected['vector_candidate_depth']}, graph candidate depth={selected['graph_candidate_depth']}.",
        f"- Held-out queries: {result['rrf_tuning']['heldout_queries']}; calibration queries: {result['rrf_tuning']['calibration_queries']}.",
        f"- Holdout delta vs vector-only: support recall {acceptance['supporting_title_recall_gain']:+.4f}; MRR {acceptance['mrr_delta']:+.4f}; nDCG {acceptance['ndcg_delta']:+.4f}; answer-string presence {acceptance['answer_text_presence_delta']:+.4f}.",
        f"- Clears predeclared retrieval gate: {acceptance['candidate_clears_retrieval_gate']} (support recall +1 pp; MRR/nDCG regressions limited to 0.02).",
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
