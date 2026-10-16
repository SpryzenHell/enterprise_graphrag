from __future__ import annotations

import re

from .fusion import Hit


ENTITY_RE = re.compile(
    r"\b[A-Z][A-Za-z0-9&.-]{2,}(?:\s+[A-Z][A-Za-z0-9&.-]{2,}){0,2}\b"
)


def extract_entities(text: str) -> list[str]:
    """Extract capped capitalized phrases plus contiguous two-word aliases.

    Wikipedia-style titles frequently extend the actual named entity with generic
    suffixes (e.g. "Project Atlas Backup Schedule"), while the body mentions only
    "Project Atlas". Adding bigrams makes those exact aliases share a tenant-scoped
    Entity node. The retrieval scorer subsequently downweights high-degree aliases
    to avoid promoting generic hubs.
    """
    seen: set[str] = set()
    entities: list[str] = []

    def add(value: str) -> None:
        value = value.strip()
        key = value.casefold()
        if len(value) < 3 or key in seen:
            return
        seen.add(key)
        entities.append(value)

    for raw in ENTITY_RE.findall(text):
        words = raw.split()
        add(raw)
        if len(words) >= 3:
            for index in range(len(words) - 1):
                add(" ".join(words[index:index + 2]))
        if len(entities) >= 48:
            break
    return entities[:48]


class Neo4jTenantStore:
    """Neo4j adapter with tenant identity and predicates on every query."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
    ) -> None:
        from neo4j import GraphDatabase

        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
        )
        self.database = database

    def verify(self) -> None:
        self.driver.verify_connectivity()

    def close(self) -> None:
        self.driver.close()

    def ensure_schema(self) -> None:
        queries = [
            (
                "CREATE CONSTRAINT document_tenant_doc IF NOT EXISTS "
                "FOR (d:Document) REQUIRE (d.tenant_id, d.doc_id) IS UNIQUE"
            ),
            (
                "CREATE CONSTRAINT entity_tenant_key IF NOT EXISTS "
                "FOR (e:Entity) REQUIRE (e.tenant_id, e.key) IS UNIQUE"
            ),
            (
                "CREATE INDEX document_tenant IF NOT EXISTS "
                "FOR (d:Document) ON (d.tenant_id)"
            ),
            (
                "CREATE INDEX entity_tenant IF NOT EXISTS "
                "FOR (e:Entity) ON (e.tenant_id)"
            ),
            (
                "CREATE FULLTEXT INDEX document_text_fulltext IF NOT EXISTS "
                "FOR (d:Document) ON EACH [d.title, d.text]"
            ),
        ]

        with self.driver.session(database=self.database) as session:
            for query in queries:
                session.run(query).consume()
            # Searches must not race the asynchronous full-text index build.
            session.run("CALL db.awaitIndexes(60)").consume()

    def add(self, tenant: str, doc: dict) -> None:
        self.add_many(tenant, [doc])

    def add_many(self, tenant: str, documents: list[dict]) -> None:
        """Bulk-upsert documents and tenant-scoped entity relationships in one query."""
        if not documents:
            return
        rows = [
            {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "text": doc["text"],
                "entities": [
                    {
                        "name": name,
                        "search_terms": sorted(
                            set(
                                token.lower()
                                for token in re.findall(r"[A-Za-z0-9]{3,}", name)
                            )
                        ),
                    }
                    # Extract title and body independently so the final capitalized
                    # token in a title cannot merge with the first entity in the
                    # body (e.g. "Schedule Project Atlas") and hide shared graph keys.
                    for name in dict.fromkeys(
                        extract_entities(doc["title"]) + extract_entities(doc["text"])
                    )
                ],
            }
            for doc in documents
        ]
        query = """
        UNWIND $documents AS item
        MERGE (d:Document {tenant_id:$tenant, doc_id:item.doc_id})
        SET d.title=item.title,
            d.text=item.text
        WITH d, item
        OPTIONAL MATCH (d)-[r:MENTIONS]->(:Entity {tenant_id:$tenant})
        DELETE r
        WITH DISTINCT d, item
        FOREACH (entity IN item.entities |
            MERGE (e:Entity {tenant_id:$tenant, key:toLower(entity.name)})
            SET e.name=entity.name,
                e.search_terms=entity.search_terms
            MERGE (d)-[:MENTIONS]->(e)
        )
        """
        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                tenant=tenant,
                documents=rows,
            ).consume()

    def expand_from_anchors(
        self,
        tenant: str,
        anchor_doc_ids: list[str],
        limit: int,
    ) -> list[Hit]:
        """Expand tenant-scoped neighbors, preferring rare entity bridges.

        FAISS determines which documents are the semantic anchors. Neo4j then
        retrieves linked supporting passages. A common entity can connect hundreds
        of unrelated documents, so score each anchor->entity->candidate path with
        an inverse-square-root entity-degree weight and the rank of its vector
        anchor. This reduces hub dominance while still rewarding evidence linked
        to multiple strong anchors.
        """
        if limit < 1 or not anchor_doc_ids:
            return []
        unique_anchor_ids = list(dict.fromkeys(str(value) for value in anchor_doc_ids if value))[:1000]
        if not unique_anchor_ids:
            return []
        anchors = [
            {"doc_id": doc_id, "rank": rank}
            for rank, doc_id in enumerate(unique_anchor_ids, start=1)
        ]
        query = """
        // First collapse all anchor paths into one row per bridge entity.
        // The bridge degree is then counted once for each entity, rather than
        // repeatedly for every anchor->candidate path sharing that entity.
        UNWIND $anchors AS seed
        MATCH (anchor:Document {tenant_id:$tenant, doc_id:seed.doc_id})
        MATCH (anchor)-[:MENTIONS]->(bridge:Entity {tenant_id:$tenant})
        WITH bridge,
             collect(DISTINCT {doc_id: anchor.doc_id, rank: seed.rank}) AS anchor_seeds
        CALL {
            WITH bridge
            MATCH (bridge)<-[:MENTIONS]-(neighbor:Document {tenant_id:$tenant})
            RETURN count(DISTINCT neighbor) AS bridge_degree
        }
        UNWIND anchor_seeds AS anchor_seed
        MATCH (bridge)<-[:MENTIONS]-(candidate:Document {tenant_id:$tenant})
        WHERE candidate.doc_id <> anchor_seed.doc_id
        WITH candidate,
             anchor_seed,
             bridge,
             bridge_degree
        WITH candidate,
             collect(DISTINCT anchor_seed.doc_id) AS anchor_docs,
             collect(DISTINCT bridge.key) AS bridge_keys,
             min(anchor_seed.rank) AS best_anchor_rank,
             sum(
                 (1.0 / sqrt(toFloat(bridge_degree)))
                 / sqrt(toFloat(anchor_seed.rank))
             ) AS rarity_seed_score
        WITH candidate,
             anchor_docs,
             bridge_keys,
             best_anchor_rank,
             rarity_seed_score,
             (
                 rarity_seed_score
                 + 0.08 * size(anchor_docs)
                 + 0.03 * size(bridge_keys)
             ) AS expansion_score
        RETURN candidate.doc_id AS doc_id,
               candidate.title AS title,
               candidate.text AS text,
               expansion_score AS score,
               anchor_docs AS anchor_docs,
               bridge_keys AS bridge_keys,
               best_anchor_rank AS best_anchor_rank,
               rarity_seed_score AS rarity_seed_score
        ORDER BY score DESC, doc_id
        LIMIT $limit
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                tenant=tenant,
                anchors=anchors,
                limit=limit,
            )
            data_method = getattr(result, "data", None)
            rows = list(data_method()) if callable(data_method) else list(result)

        return [
            Hit(
                doc_id=row["doc_id"],
                title=row["title"],
                tenant_id=tenant,
                text=row["text"],
                score=float(row["score"]),
                source="graph",
                metadata={
                    "doc_id": row["doc_id"],
                    "title": row["title"],
                    "text": row["text"],
                    "traversal_hops": 2,
                    "traversal_score": float(row["score"]),
                    "anchor_docs": list(row["anchor_docs"] or []),
                    "bridge_entities": list(row["bridge_keys"] or []),
                    "best_anchor_rank": int(row["best_anchor_rank"]),
                    "bridge_rarity_score": float(row["rarity_seed_score"]),
                    "retrieval_path": "vector_seeded_two_hop",
                    "bridge_scoring": "inverse_sqrt_degree_x_inverse_sqrt_anchor_rank",
                },
            )
            for row in rows
        ]

    def search(
        self,
        tenant: str,
        query_text: str,
        limit: int,
    ) -> list[Hit]:
        """Use indexed full-text retrieval and tenant-filtered two-hop graph traversal.

        Full-text scores give graph-only retrieval a useful lexical ranking rather than
        assigning nearly identical scores to documents that happen to contain common
        query tokens. Tenant filtering remains inside each Cypher query, before rows
        are returned to the application. The second path adds linked evidence that
        need not repeat the original query terms.
        """
        terms = [
            token.lower()
            for token in re.findall(r"[A-Za-z0-9]{3,}", query_text)
        ][:12]
        if not terms or limit < 1:
            return []

        # Every term is generated from an ASCII alphanumeric regex, then quoted for
        # Lucene. OR recall is important for questions where relevant evidence shares
        # only one or two content words with the user query.
        fulltext_query = " OR ".join(f'"{term}"' for term in terms)

        direct_query = """
        CALL db.index.fulltext.queryNodes(
            "document_text_fulltext",
            $fulltext_query
        )
        YIELD node AS d, score AS lexical_score
        WHERE d.tenant_id = $tenant
        OPTIONAL MATCH (d)-[:MENTIONS]->(e:Entity {tenant_id:$tenant})
        WITH d, lexical_score, collect(DISTINCT e.name) AS entity_names
        WITH d,
             lexical_score
             + 0.15 * size([
                 term IN $terms
                 WHERE any(name IN entity_names WHERE toLower(name) CONTAINS term)
             ])
             + 0.05 * size([
                 term IN $terms
                 WHERE toLower(d.title) CONTAINS term
             ]) AS score
        RETURN d.doc_id AS doc_id,
               d.title AS title,
               d.text AS text,
               score AS score
        ORDER BY score DESC, doc_id
        LIMIT $limit
        """

        # Bounded two-hop traversal:
        # query-matched entity -> anchor document -> shared entity -> candidate doc.
        # Indexed entity tokens avoid scanning every entity name with CONTAINS.
        traversal_query = """
        // Start from a small, ranked set of text-relevant anchor documents, then
        // expand their tenant-scoped entity edges. This avoids a tenant-wide scan
        // over every Entity node and reliably finds related evidence whose own text
        // does not repeat the user's query terms.
        CALL db.index.fulltext.queryNodes(
            "document_text_fulltext",
            $fulltext_query
        )
        YIELD node AS anchor, score AS anchor_score
        WHERE anchor.tenant_id = $tenant
        WITH anchor, anchor_score
        ORDER BY anchor_score DESC
        LIMIT $anchor_limit
        MATCH (anchor)-[:MENTIONS]->(bridge:Entity {tenant_id:$tenant})
        MATCH (bridge)<-[:MENTIONS]-(candidate:Document {tenant_id:$tenant})
        WHERE candidate.doc_id <> anchor.doc_id
        WITH candidate,
             collect(DISTINCT anchor.doc_id) AS anchor_docs,
             collect(DISTINCT bridge.key) AS bridge_keys,
             max(anchor_score) AS best_anchor_score
        RETURN candidate.doc_id AS doc_id,
               candidate.title AS title,
               candidate.text AS text,
               (best_anchor_score
                + 0.1 * size(anchor_docs)
                + 0.05 * size(bridge_keys)) AS score,
               anchor_docs AS anchor_docs,
               bridge_keys AS bridge_keys
        ORDER BY score DESC, doc_id
        LIMIT $limit
        """

        def collect_rows(result) -> list:
            data_method = getattr(result, "data", None)
            if callable(data_method):
                return list(data_method())
            try:
                return list(result)
            except TypeError:
                return []

        with self.driver.session(database=self.database) as session:
            direct_rows = collect_rows(
                session.run(
                    direct_query,
                    tenant=tenant,
                    terms=terms,
                    fulltext_query=fulltext_query,
                    limit=limit,
                )
            )
            traversal_rows = collect_rows(
                session.run(
                    traversal_query,
                    tenant=tenant,
                    fulltext_query=fulltext_query,
                    anchor_limit=max(50, limit * 5),
                    limit=limit,
                )
            )

        hits_by_id: dict[str, Hit] = {}
        for row in direct_rows:
            doc_id = row["doc_id"]
            hits_by_id[doc_id] = Hit(
                doc_id=doc_id,
                title=row["title"],
                tenant_id=tenant,
                text=row["text"],
                score=float(row["score"]),
                source="graph",
                metadata={
                    "doc_id": doc_id,
                    "title": row["title"],
                    "text": row["text"],
                    "traversal_hops": 0,
                    "traversal_score": 0.0,
                    "retrieval_path": "fulltext",
                },
            )

        for row in traversal_rows:
            doc_id = row["doc_id"]
            traversal_score = float(row["score"])
            if doc_id in hits_by_id:
                hit = hits_by_id[doc_id]
                hits_by_id[doc_id] = Hit(
                    doc_id=hit.doc_id,
                    title=hit.title,
                    tenant_id=hit.tenant_id,
                    text=hit.text,
                    score=hit.score + 0.5 * traversal_score,
                    source=hit.source,
                    metadata={
                        **hit.metadata,
                        "traversal_score": traversal_score,
                        "traversal_hops": 2,
                        "anchor_docs": row["anchor_docs"],
                        "bridge_entities": row["bridge_keys"],
                        "retrieval_path": "fulltext+two_hop",
                    },
                )
            else:
                hits_by_id[doc_id] = Hit(
                    doc_id=doc_id,
                    title=row["title"],
                    tenant_id=tenant,
                    text=row["text"],
                    score=traversal_score,
                    source="graph",
                    metadata={
                        "doc_id": doc_id,
                        "title": row["title"],
                        "text": row["text"],
                        "traversal_hops": 2,
                        "traversal_score": traversal_score,
                        "anchor_docs": row["anchor_docs"],
                        "bridge_entities": row["bridge_keys"],
                        "retrieval_path": "two_hop",
                    },
                )

        return sorted(
            hits_by_id.values(),
            key=lambda hit: (-hit.score, hit.doc_id),
        )[:limit]

    def trace(
        self,
        tenant: str,
        doc_ids: list[str],
    ) -> dict:
        if not doc_ids:
            return {"nodes": [], "edges": []}

        query = """
        MATCH (d:Document {tenant_id:$tenant})
        WHERE d.doc_id IN $doc_ids
        OPTIONAL MATCH (d)-[:MENTIONS]->(e:Entity {tenant_id:$tenant})
        RETURN d.doc_id AS doc_id,
               d.title AS title,
               e.key AS entity_key,
               e.name AS entity_name
        """

        nodes = {}
        edges = []

        with self.driver.session(database=self.database) as session:
            rows = session.run(
                query,
                tenant=tenant,
                doc_ids=doc_ids,
            )
            for row in rows:
                document_id = row["doc_id"]
                nodes[document_id] = {
                    "id": document_id,
                    "label": row["title"],
                    "type": "document",
                    "tenant_id": tenant,
                }

                entity_key = row.get("entity_key")
                entity_name = row.get("entity_name")
                if entity_key is not None and entity_name is not None:
                    entity_id = (
                        f"entity:{tenant}:{entity_key}"
                    )
                    nodes[entity_id] = {
                        "id": entity_id,
                        "label": entity_name,
                        "type": "entity",
                        "tenant_id": tenant,
                    }
                    edges.append(
                        {
                            "source": document_id,
                            "target": entity_id,
                            "type": "MENTIONS",
                        }
                    )

        return {
            "nodes": list(nodes.values()),
            "edges": edges,
        }
