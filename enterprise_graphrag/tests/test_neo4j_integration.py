import os
import time

import pytest

from enterprise_graphrag.neo4j_store import Neo4jTenantStore


@pytest.mark.integration
def test_neo4j_tenant_isolation():
    uri = os.getenv("NEO4J_URI")
    password = os.getenv("NEO4J_PASSWORD")

    if not uri or not password:
        pytest.skip("NEO4J_URI/NEO4J_PASSWORD not configured")

    store = Neo4jTenantStore(
        uri,
        os.getenv("NEO4J_USER", "neo4j"),
        password,
        os.getenv("NEO4J_DATABASE", "neo4j"),
    )

    try:
        for _ in range(30):
            try:
                store.verify()
                break
            except Exception:
                time.sleep(1)
        else:
            pytest.fail("Neo4j did not become ready")

        store.ensure_schema()
        store.add(
            "acme",
            {
                "doc_id": "integration-acme",
                "title": "Acme Integration Policy",
                "text": "Acme Security Operations owns incident response.",
            },
        )
        store.add(
            "globex",
            {
                "doc_id": "integration-globex",
                "title": "Globex Integration Policy",
                "text": "Globex Risk Operations owns incident response.",
            },
        )

        hits = store.search(
            "acme",
            "Security Operations",
            10,
        )

        assert hits
        assert all(
            hit.tenant_id == "acme"
            for hit in hits
        )
        assert all(
            hit.doc_id != "integration-globex"
            for hit in hits
        )

        store.add(
            "acme",
            {
                "doc_id": "integration-acme",
                "title": "Acme Integration Policy v2",
                "text": "Acme Finance Operations owns incident response.",
            },
        )

        stale_hits = store.search(
            "acme",
            "Security Operations",
            10,
        )
        updated_hits = store.search(
            "acme",
            "Finance Operations",
            10,
        )

        assert all(
            hit.doc_id != "integration-acme"
            for hit in stale_hits
        )
        assert any(
            hit.doc_id == "integration-acme"
            for hit in updated_hits
        )

        trace = store.trace(
            "acme",
            ["integration-acme"],
        )

        assert trace["nodes"]
        assert all(
            node["tenant_id"] == "acme"
            for node in trace["nodes"]
        )
    finally:
        store.close()
