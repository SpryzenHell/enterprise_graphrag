from __future__ import annotations

import re


class Neo4jTenantStore:
    """Neo4j adapter. Every identity and traversal is tenant constrained."""
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        self.driver.close()

    def ensure_schema(self):
        queries = [
            "CREATE CONSTRAINT document_tenant_doc IF NOT EXISTS FOR (d:Document) REQUIRE (d.tenant_id, d.doc_id) IS UNIQUE",
            "CREATE CONSTRAINT entity_tenant_key IF NOT EXISTS FOR (e:Entity) REQUIRE (e.tenant_id, e.key) IS UNIQUE",
            "CREATE INDEX document_tenant IF NOT EXISTS FOR (d:Document) ON (d.tenant_id)",
            "CREATE INDEX entity_tenant IF NOT EXISTS FOR (e:Entity) ON (e.tenant_id)",
        ]
        with self.driver.session(database=self.database) as s:
            for query in queries:
                s.run(query).consume()

    def upsert_document(self, tenant: str, doc_id: str, title: str, text: str, entities: list[str]):
        query = """
        MERGE (d:Document {tenant_id:$tenant, doc_id:$doc_id})
        SET d.title=$title, d.text=$text
        WITH d
        UNWIND $entities AS name
        MERGE (e:Entity {tenant_id:$tenant, key:toLower(name)})
        SET e.name=name
        MERGE (d)-[:MENTIONS]->(e)
        """
        with self.driver.session(database=self.database) as s:
            s.run(query, tenant=tenant, doc_id=doc_id, title=title, text=text, entities=entities).consume()

    def search(self, tenant: str, query_text: str, limit: int = 8):
        terms = [x.lower() for x in re.findall(r"[A-Za-z0-9]{3,}", query_text)][:12]
        query = """
        MATCH (d:Document {tenant_id:$tenant})-[:MENTIONS]->(e:Entity {tenant_id:$tenant})
        WHERE any(term IN $terms WHERE toLower(e.name) CONTAINS term)
           OR any(term IN $terms WHERE toLower(d.text) CONTAINS term)
        RETURN d.doc_id AS doc_id, d.title AS title, d.text AS text,
               count(DISTINCT e) AS entity_hits
        ORDER BY entity_hits DESC, d.doc_id
        LIMIT $limit
        """
        with self.driver.session(database=self.database) as s:
            return list(s.run(query, tenant=tenant, terms=terms, limit=limit))
