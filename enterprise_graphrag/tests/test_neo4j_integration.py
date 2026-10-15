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
            "Security",
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
            "Security",
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



@pytest.mark.integration
def test_neo4j_bulk_upsert_and_tenant_isolation():
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
        store.add_many(
            "acme",
            [
                {
                    "doc_id": "bulk-integration-acme-1",
                    "title": "Acme Bulk Security Policy",
                    "text": "Acme Security Operations owns account recovery.",
                },
                {
                    "doc_id": "bulk-integration-acme-2",
                    "title": "Acme Bulk Incident Policy",
                    "text": "Acme Incident Response retains reports for 365 days.",
                },
            ],
        )
        store.add_many(
            "globex",
            [
                {
                    "doc_id": "bulk-integration-globex-1",
                    "title": "Globex Bulk Security Policy",
                    "text": "Globex Risk Operations owns external reviews.",
                },
            ],
        )

        acme_hits = store.search("acme", "Security Operations", 10)
        assert any(hit.doc_id == "bulk-integration-acme-1" for hit in acme_hits)
        assert all(hit.tenant_id == "acme" for hit in acme_hits)
        assert all(hit.doc_id != "bulk-integration-globex-1" for hit in acme_hits)

        store.add_many(
            "acme",
            [
                {
                    "doc_id": "bulk-integration-acme-1",
                    "title": "Acme Bulk Finance Policy",
                    "text": "Acme Finance Operations owns account recovery.",
                },
            ],
        )
        # Query only for the removed term; "Operations" remains in the replacement document.
        stale_hits = store.search("acme", "Security", 10)
        updated_hits = store.search("acme", "Finance Operations", 10)
        assert all(hit.doc_id != "bulk-integration-acme-1" for hit in stale_hits)
        assert any(hit.doc_id == "bulk-integration-acme-1" for hit in updated_hits)

        trace = store.trace("acme", ["bulk-integration-acme-1"])
        assert trace["nodes"]
        assert all(node["tenant_id"] == "acme" for node in trace["nodes"])
    finally:
        store.close()



@pytest.mark.integration
def test_neo4j_two_hop_retrieval_returns_linked_evidence_and_stays_tenant_scoped():
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
        store.add_many(
            "twohop-acme",
            [
                {
                    "doc_id": "twohop-anchor-acme",
                    "title": "Incident Response Runbook",
                    "text": "The incident response owner coordinates recovery with Project Atlas.",
                },
                {
                    "doc_id": "twohop-related-acme",
                    "title": "Project Atlas Backup Schedule",
                    "text": "Project Atlas backups run nightly and retain recovery snapshots for 90 days.",
                },
            ],
        )
        store.add_many(
            "twohop-globex",
            [
                {
                    "doc_id": "twohop-related-globex",
                    "title": "Project Atlas Backup Schedule",
                    "text": "Project Atlas backups run hourly and retain Globex snapshots for 30 days.",
                },
            ],
        )

        hits = store.search("twohop-acme", "incident response", 10)
        related = next((hit for hit in hits if hit.doc_id == "twohop-related-acme"), None)
        assert related is not None, [hit.doc_id for hit in hits]
        assert related.tenant_id == "twohop-acme"
        assert related.metadata.get("traversal_hops") == 2
        assert related.metadata.get("retrieval_path") in {"two_hop", "fulltext+two_hop"}
        assert "90 days" in related.text
        assert all(hit.doc_id != "twohop-related-globex" for hit in hits)
        assert all(hit.tenant_id == "twohop-acme" for hit in hits)
    finally:
        store.close()
