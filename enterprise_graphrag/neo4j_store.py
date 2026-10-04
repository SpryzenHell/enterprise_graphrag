from __future__ import annotations

import re

from .fusion import Hit


ENTITY_RE = re.compile(
    r"\b[A-Z][A-Za-z0-9&.-]{2,}(?:\s+[A-Z][A-Za-z0-9&.-]{2,}){0,2}\b"
)


def extract_entities(text: str) -> list[str]:
    seen = set()
    entities = []
    for raw in ENTITY_RE.findall(text):
        value = raw.strip()
        key = value.lower()
        if key not in seen:
            seen.add(key)
            entities.append(value)
    return entities[:24]


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
        ]

        with self.driver.session(database=self.database) as session:
            for query in queries:
                session.run(query).consume()

    def add(self, tenant: str, doc: dict) -> None:
        entities = extract_entities(doc["text"])
        query = """
        MERGE (d:Document {tenant_id:$tenant, doc_id:$doc_id})
        SET d.title=$title, d.text=$text
        WITH d
        OPTIONAL MATCH (d)-[r:MENTIONS]->(:Entity {tenant_id:$tenant})
        DELETE r
        WITH d
        UNWIND $entities AS name
        MERGE (e:Entity {tenant_id:$tenant, key:toLower(name)})
        SET e.name=name
        MERGE (d)-[:MENTIONS]->(e)
        """
        with self.driver.session(database=self.database) as session:
            session.run(
                query,
                tenant=tenant,
                doc_id=doc["doc_id"],
                title=doc["title"],
                text=doc["text"],
                entities=entities,
            ).consume()

    def search(
        self,
        tenant: str,
        query_text: str,
        limit: int,
    ) -> list[Hit]:
        terms = [
            token.lower()
            for token in re.findall(
                r"[A-Za-z0-9]{3,}",
                query_text,
            )
        ][:12]
        if not terms:
            return []

        query = """
        MATCH (d:Document {tenant_id:$tenant})
        OPTIONAL MATCH (d)-[:MENTIONS]->(e:Entity {tenant_id:$tenant})
        WITH d, collect(DISTINCT e.name) AS entity_names
        WITH d,
             size([
                 term IN $terms
                 WHERE any(name IN entity_names WHERE toLower(name) CONTAINS term)
             ]) AS entity_hits,
             size([
                 term IN $terms
                 WHERE toLower(d.title) CONTAINS term
             ]) AS title_hits,
             size([
                 term IN $terms
                 WHERE toLower(d.text) CONTAINS term
             ]) AS text_hits
        WHERE entity_hits + title_hits + text_hits > 0
        RETURN d.doc_id AS doc_id,
               d.title AS title,
               d.text AS text,
               (2.0 * entity_hits + 0.5 * title_hits + 0.1 * text_hits) AS score
        ORDER BY score DESC, doc_id
        LIMIT $limit
        """

        with self.driver.session(database=self.database) as session:
            rows = session.run(
                query,
                tenant=tenant,
                terms=terms,
                limit=limit,
            )
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
                    },
                )
                for row in rows
            ]

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
