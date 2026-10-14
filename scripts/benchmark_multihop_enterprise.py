from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer

from enterprise_graphrag.fusion import weighted_rrf
from enterprise_graphrag.neo4j_store import Neo4jTenantStore
from enterprise_graphrag.vector_faiss import TenantFAISS

MODEL_DEFAULT = "BAAI/bge-base-en-v1.5"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
LICENSE_NOTE = "Generated synthetic benchmark data; no external corpus rows are redistributed."


class SentenceTransformerEmbedder:
    def __init__(self, model):
        self.model = model
        self.dimension = int(model.get_sentence_embedding_dimension())

    def embed(self, texts):
        encoded = [
            QUERY_PREFIX + text if "\n" not in text else text
            for text in texts
        ]
        result = self.model.encode(
            encoded,
            batch_size=64,
            convert_to_numpy=True,
            normalize_embeddings=False,
            show_progress_bar=False,
        )
        return result.tolist()


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * fraction + 0.999999)))
    return round(float(ordered[index]), 4)


def latency_summary(values):
    return {
        "n": len(values),
        "p50_ms": percentile(values, 0.50),
        "p95_ms": percentile(values, 0.95),
        "max_ms": round(max(values), 4) if values else None,
        "mean_ms": round(statistics.mean(values), 4) if values else None,
    }


def metrics(rankings, qrels):
    values = []
    for query_id, ranking in rankings.items():
        target = qrels[query_id]
        rank = next((index for index, doc_id in enumerate(ranking, start=1) if doc_id == target), None)
        values.append({
            "recall@1": 1.0 if rank is not None and rank <= 1 else 0.0,
            "recall@5": 1.0 if rank is not None and rank <= 5 else 0.0,
            "recall@10": 1.0 if rank is not None and rank <= 10 else 0.0,
            "mrr@10": 1.0 / rank if rank is not None and rank <= 10 else 0.0,
            "ndcg@10": 1.0 / __import__("math").log2(rank + 1) if rank is not None and rank <= 10 else 0.0,
            "rank": rank,
        })
    count = max(len(values), 1)
    return {
        "n_queries": len(values),
        "recall@1": round(sum(v["recall@1"] for v in values) / count, 6),
        "recall@5": round(sum(v["recall@5"] for v in values) / count, 6),
        "recall@10": round(sum(v["recall@10"] for v in values) / count, 6),
        "mrr@10": round(sum(v["mrr@10"] for v in values) / count, 6),
        "ndcg@10": round(sum(v["ndcg@10"] for v in values) / count, 6),
        "gold_rank_distribution": {
            str(rank): sum(value["rank"] == rank for value in values)
            for rank in sorted({value["rank"] for value in values if value["rank"] is not None})
        },
    }


def build_corpus(n_queries, seed):
    rng = random.Random(seed)
    division_words = [
        ("Willow", "Harbor"), ("Cedar", "Summit"), ("Maple", "Ridge"),
        ("Silver", "Meadow"), ("Amber", "Valley"), ("Quartz", "Grove"),
        ("Copper", "Canyon"), ("Juniper", "Point"), ("Saffron", "Lake"),
        ("Orchid", "Field"), ("Indigo", "Brook"), ("Granite", "Shore"),
        ("Velvet", "Forest"), ("Kestrel", "Garden"), ("Marble", "Coast"),
        ("Cobalt", "Prairie"), ("Autumn", "Creek"), ("Boulder", "Isle"),
        ("Lantern", "Hollow"), ("Pine", "Terrace"), ("Cloud", "Pavilion"),
        ("Frost", "Orchard"), ("Meadow", "Bridge"), ("Crown", "Cliff"),
        ("Cypress", "Beacon"), ("Thistle", "Bay"), ("Coral", "Glen"),
        ("Aster", "Point"), ("Mica", "Garden"), ("Birch", "Landing"),
        ("Opal", "Falls"), ("Dawn", "Court"), ("Elm", "Station"),
        ("Linen", "Heights"), ("Cinder", "Crossing"), ("Basil", "Run"),
        ("Tundra", "Walk"), ("Pearl", "Circle"), ("Ash", "Harbor"),
        ("Lumen", "Trail"),
    ]
    rng.shuffle(division_words)
    corpus = []
    queries = {}
    qrels = {}
    for index in range(n_queries):
        code = f"KRYPTON-{index + 1:03d}"
        first, second = division_words[index % len(division_words)]
        division = f"{first} {second}"
        days = rng.choice((45, 90, 180, 270, 365))
        anchor_id = f"system-anchor-{index:03d}"
        target_id = f"division-policy-{index:03d}"
        corpus.append({
            "doc_id": anchor_id,
            "title": f"System {code} ownership register",
            "text": f"System {code} is administered by Division {division}. The register lists its controlling division and service owner.",
        })
        corpus.append({
            "doc_id": target_id,
            "title": f"Division {division} archive schedule R-{index + 1:03d}",
            "text": f"Division {division} records office: the archive duration for operational packets is {days} days under schedule R-{index + 1:03d}.",
        })
        queries[f"query-{index:03d}"] = {
            "query": f"What is the archive duration associated with System {code}?",
            "target": target_id,
            "anchor": anchor_id,
            "division": division,
        }
        qrels[f"query-{index:03d}"] = target_id

    # Hard lexical negatives share the general task vocabulary but are not connected
    # to any queried system's controlling division.
    for index in range(n_queries * 2):
        days = rng.choice((30, 60, 120, 240, 400))
        corpus.append({
            "doc_id": f"generic-schedule-{index:03d}",
            "title": f"Generic archive duration schedule G-{index + 1:03d}",
            "text": f"General operations records office: the archive duration for operational packets is {days} days under schedule G-{index + 1:03d}.",
        })
    return corpus, queries, qrels


def select_config_on_calibration(rankings_by_config, query_ids, qrels):
    shuffled = list(query_ids)
    random.Random(20261014 + 31).shuffle(shuffled)
    midpoint = max(1, len(shuffled) // 2)
    calibration_ids, holdout_ids = shuffled[:midpoint], shuffled[midpoint:]
    if not holdout_ids:
        calibration_ids, holdout_ids = shuffled, shuffled

    records = []
    for depth in (10, 20, 30):
        for vector_weight in (0.55, 0.75, 0.90, 0.95, 0.99, 1.00):
            by_query = {}
            for query_id in query_ids:
                vector_hits = rankings_by_config["vector"][query_id][:depth]
                graph_hits = rankings_by_config["neo4j"][query_id][:depth]
                fused = weighted_rrf(
                    {"vector": vector_hits, "graph": graph_hits},
                    {"vector": vector_weight, "graph": 1.0 - vector_weight},
                    k=60,
                    limit=10,
                )
                by_query[query_id] = [hit.doc_id for hit in fused]
            records.append({
                "candidate_limit": depth,
                "vector_weight": vector_weight,
                "graph_weight": round(1 - vector_weight, 2),
                "vector_only_control": vector_weight == 1.0,
                "calibration_metrics": metrics(
                    {qid: by_query[qid] for qid in calibration_ids},
                    {qid: qrels[qid] for qid in calibration_ids},
                ),
                "holdout_metrics": metrics(
                    {qid: by_query[qid] for qid in holdout_ids},
                    {qid: qrels[qid] for qid in holdout_ids},
                ),
            })

    hybrids = [record for record in records if not record["vector_only_control"]]
    selected = max(
        hybrids,
        key=lambda record: (
            record["calibration_metrics"]["mrr@10"],
            record["calibration_metrics"]["ndcg@10"],
            record["calibration_metrics"]["recall@10"],
            record["vector_weight"],
            -record["candidate_limit"],
        ),
    )
    vector_control = max(
        [record for record in records if record["vector_only_control"]],
        key=lambda record: (
            record["calibration_metrics"]["mrr@10"],
            record["calibration_metrics"]["ndcg@10"],
            record["calibration_metrics"]["recall@10"],
            -record["candidate_limit"],
        ),
    )
    return {
        "selection_rule": "On calibration queries, maximize MRR@10, then nDCG@10, then Recall@10; ties prefer more vector weight and the smaller candidate pool.",
        "calibration_query_count": len(calibration_ids),
        "holdout_query_count": len(holdout_ids),
        "selected_hybrid": selected,
        "vector_only_control": vector_control,
        "all_configs": records,
        "warning": "This is a generated diagnostic benchmark for multi-hop entity linking, not a public standard benchmark. The split is held out by query after a fixed-seed corpus generation.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/enterprise-multihop")
    parser.add_argument("--num-queries", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20261014)
    parser.add_argument("--embedding-model", default=os.getenv("GRAGRAPH_EMBEDDING_MODEL", MODEL_DEFAULT))
    parser.add_argument("--tenant", default="multihop-enterprise-eval")
    args = parser.parse_args()

    uri = os.getenv("NEO4J_URI", "")
    password = os.getenv("NEO4J_PASSWORD", "")
    if not uri or not password:
        raise SystemExit("NEO4J_URI and NEO4J_PASSWORD are required to measure actual Neo4j traversal")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    start_utc = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    corpus, queries, qrels = build_corpus(args.num_queries, args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(args.embedding_model, device=device)
    embedder = SentenceTransformerEmbedder(model)
    store = Neo4jTenantStore(
        uri,
        os.getenv("NEO4J_USER", "neo4j"),
        password,
        os.getenv("NEO4J_DATABASE", "neo4j"),
    )
    result = {
        "schema_version": 1,
        "started_utc": start_utc,
        "seed": args.seed,
        "embedding_model": args.embedding_model,
        "embedding_model_license": "MIT" if args.embedding_model.startswith("BAAI/bge") else "See model card",
        "embedding_device": device,
        "synthetic_data_note": LICENSE_NOTE,
        "corpus_documents": len(corpus),
        "query_count": len(queries),
    }

    try:
        for _ in range(30):
            try:
                store.verify()
                break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError("Neo4j did not become ready in 30 seconds")
        store.ensure_schema()
        with tempfile.TemporaryDirectory(prefix="enterprise-multihop-faiss-") as temp:
            vector = TenantFAISS(str(Path(temp) / "faiss"), embedder)
            start = time.perf_counter()
            vector.add(args.tenant, corpus)
            vector_index_seconds = time.perf_counter() - start

            start = time.perf_counter()
            store.add_many(args.tenant, corpus)
            graph_index_seconds = time.perf_counter() - start

            qids = sorted(queries)
            warm_id = qids[0]
            warm_query = queries[warm_id]["query"]
            embedder.embed(["multihop benchmark warm-up"])
            vector.search(args.tenant, warm_query, 30)
            store.search(args.tenant, warm_query, 30)

            vector_rankings = {}
            graph_rankings = {}
            latencies = {"vector_top30_ms": [], "neo4j_top30_ms": []}
            graph_hops = {}
            for qid in qids:
                query = queries[qid]["query"]
                start = time.perf_counter()
                vector_hits = vector.search(args.tenant, query, 30)
                latencies["vector_top30_ms"].append((time.perf_counter() - start) * 1000)
                start = time.perf_counter()
                graph_hits = store.search(args.tenant, query, 30)
                latencies["neo4j_top30_ms"].append((time.perf_counter() - start) * 1000)
                vector_rankings[qid] = vector_hits
                graph_rankings[qid] = graph_hits
                target = qrels[qid]
                target_hit = next((hit for hit in graph_hits if hit.doc_id == target), None)
                graph_hops[qid] = target_hit.metadata.get("traversal_hops") if target_hit else None

            rankings = {"vector": vector_rankings, "neo4j": graph_rankings}
            vector_ids = {qid: [hit.doc_id for hit in hits] for qid, hits in vector_rankings.items()}
            graph_ids = {qid: [hit.doc_id for hit in hits] for qid, hits in graph_rankings.items()}
            sweep = select_config_on_calibration(rankings, qids, qrels)
            config = sweep["selected_hybrid"]
            selected_ranks = {}
            for qid in qids:
                fused = weighted_rrf(
                    {
                        "vector": vector_rankings[qid][:config["candidate_limit"]],
                        "graph": graph_rankings[qid][:config["candidate_limit"]],
                    },
                    {"vector": config["vector_weight"], "graph": config["graph_weight"]},
                    k=60,
                    limit=10,
                )
                selected_ranks[qid] = [hit.doc_id for hit in fused]

            all_config_mrr = {
                f"vector={r['vector_weight']:.2f},depth={r['candidate_limit']}": r["holdout_metrics"]["mrr@10"]
                for r in sweep["all_configs"]
            }
            result.update({
                "vector_index_build_seconds": round(vector_index_seconds, 4),
                "neo4j_index_build_seconds": round(graph_index_seconds, 4),
                "vector_only_metrics_all_queries": metrics(vector_ids, qrels),
                "neo4j_graph_only_metrics_all_queries": metrics(graph_ids, qrels),
                "selected_hybrid_metrics_all_queries": metrics(selected_ranks, qrels),
                "holdout_vector_only_metrics": sweep["vector_only_control"]["holdout_metrics"],
                "holdout_selected_hybrid_metrics": sweep["selected_hybrid"]["holdout_metrics"],
                "candidate_weight_depth_sweep": sweep,
                "target_two_hop_count": sum(value == 2 for value in graph_hops.values()),
                "target_returned_count": sum(value is not None for value in graph_hops.values()),
                "target_hop_distribution": {
                    str(hops): sum(value == hops for value in graph_hops.values())
                    for hops in sorted({value for value in graph_hops.values() if value is not None})
                },
                "query_latency": {name: latency_summary(values) for name, values in latencies.items()},
                "elapsed_seconds": round(time.perf_counter() - t0, 4),
            })
    finally:
        store.close()

    result["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (output_dir / "enterprise_multihop.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    chosen = result["candidate_weight_depth_sweep"]["selected_hybrid"]
    control = result["candidate_weight_depth_sweep"]["vector_only_control"]
    lines = [
        "# Enterprise multi-hop retrieval diagnostic",
        "",
        f"- Started UTC: {result['started_utc']}",
        f"- Completed UTC: {result['completed_utc']}",
        f"- Runtime seconds: {result['elapsed_seconds']}",
        f"- Model: {result['embedding_model']} ({result['embedding_model_license']}); device={result['embedding_device']}",
        f"- Corpus documents: {result['corpus_documents']}; queries: {result['query_count']}; seed={args.seed}",
        f"- Dataset license note: {LICENSE_NOTE}",
        "",
        "| Method (all queries) | Recall@1 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, key in (
        ("FAISS vector-only", "vector_only_metrics_all_queries"),
        ("Neo4j graph-only + two-hop", "neo4j_graph_only_metrics_all_queries"),
        ("Selected weighted RRF", "selected_hybrid_metrics_all_queries"),
    ):
        m = result[key]
        lines.append(f"| {label} | {m['recall@1']:.4f} | {m['recall@5']:.4f} | {m['recall@10']:.4f} | {m['mrr@10']:.4f} | {m['ndcg@10']:.4f} |")
    lines += [
        "",
        "## Held-out selection",
        "",
        f"- Calibration queries: {result['candidate_weight_depth_sweep']['calibration_query_count']}; held-out queries: {result['candidate_weight_depth_sweep']['holdout_query_count']}.",
        f"- Selected hybrid weight/depth: vector={chosen['vector_weight']:.2f}, graph={chosen['graph_weight']:.2f}, candidate_depth={chosen['candidate_limit']}.",
        f"- Selected hybrid holdout MRR@10={chosen['holdout_metrics']['mrr@10']:.4f}; nDCG@10={chosen['holdout_metrics']['ndcg@10']:.4f}; Recall@10={chosen['holdout_metrics']['recall@10']:.4f}.",
        f"- Vector-only control holdout MRR@10={control['holdout_metrics']['mrr@10']:.4f}; nDCG@10={control['holdout_metrics']['ndcg@10']:.4f}; Recall@10={control['holdout_metrics']['recall@10']:.4f}.",
        f"- Gold target retrieved via two-hop graph metadata: {result['target_two_hop_count']} / {result['query_count']}; any graph result for gold: {result['target_returned_count']}.",
        "",
        "| Query path | P50 ms | P95 ms | Max ms |",
        "|---|---:|---:|---:|",
    ]
    for name, latency in result["query_latency"].items():
        lines.append(f"| {name} | {latency['p50_ms']} | {latency['p95_ms']} | {latency['max_ms']} |")
    lines += [
        "",
        f"> {sweep['warning'] if 'sweep' in locals() else result['candidate_weight_depth_sweep']['warning']}",
        "",
        "This synthetic test is designed to verify multi-hop entity linking when relevant documents omit the queried system name. It complements, but does not replace, the BEIR SciFact ranking benchmark.",
    ]
    (output_dir / "enterprise_multihop.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
