import os
import time

import pytest

from enterprise_graphrag.neo4j_store import Neo4jTenantStore, extract_entities


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


@pytest.mark.integration
def test_vector_seeded_two_hop_expansion_retrieves_related_tenant_document():
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
            "vector-seed-acme",
            [
                {
                    "doc_id": "vector-seed-anchor",
                    "title": "Acme Incident Response",
                    "text": "Acme coordinates recovery with Helios Analytics after incidents.",
                },
                {
                    "doc_id": "vector-seed-related",
                    "title": "Telemetry Operations",
                    "text": "Helios Analytics supplies orbital telemetry through Orion Instruments.",
                },
            ],
        )
        store.add(
            "vector-seed-globex",
            {
                "doc_id": "vector-seed-globex-related",
                "title": "Telemetry Operations",
                "text": "Helios Analytics supplies telemetry to Globex operations.",
            },
        )

        # Both documents are in the vector candidate pool. A second anchor should
        # be allowed to return the first as graph-linked evidence; the graph result
        # is then deduplicated by RRF instead of being suppressed as an "anchor".
        expanded = store.expand_from_anchors(
            "vector-seed-acme",
            ["vector-seed-anchor", "vector-seed-related"],
            10,
        )
        by_id = {hit.doc_id: hit for hit in expanded}
        assert "vector-seed-related" in by_id, [
            (hit.doc_id, hit.metadata) for hit in expanded
        ]
        assert by_id["vector-seed-related"].metadata["retrieval_path"] == "vector_seeded_two_hop"
        assert by_id["vector-seed-related"].metadata["traversal_hops"] == 2
        assert by_id["vector-seed-related"].metadata["best_anchor_rank"] == 1
        assert all(hit.tenant_id == "vector-seed-acme" for hit in expanded)
        assert "vector-seed-globex-related" not in by_id
    finally:
        store.close()


@pytest.mark.integration
def test_vector_seeded_expansion_penalizes_high_degree_entity_hubs():
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
            "rarity-acme",
            [
                {
                    "doc_id": "rarity-anchor",
                    "title": "incident recovery anchor",
                    "text": "the recovery workflow links Helios Analytics and Project Obsidian Gateway.",
                },
                {
                    "doc_id": "rarity-target",
                    "title": "credential escrow instructions",
                    "text": "credential escrow is managed through Project Obsidian Gateway.",
                },
                *[
                    {
                        "doc_id": f"hub-candidate-{i:02d}",
                        "title": f"routine monitor {i:02d}",
                        "text": f"Helios Analytics monitors routine queue number {i}.",
                    }
                    for i in range(14)
                ],
            ],
        )
        # A similarly named entity in a separate tenant must not affect degree,
        # candidates, or ranking in this tenant.
        store.add(
            "rarity-globex",
            {
                "doc_id": "hub-cross-tenant",
                "title": "external credential system",
                "text": "Project Obsidian Gateway handles Globex external access.",
            },
        )

        hits = store.expand_from_anchors("rarity-acme", ["rarity-anchor"], 20)
        assert hits, "two-hop expansion returned no candidates"
        assert hits[0].doc_id == "rarity-target", [
            (hit.doc_id, hit.metadata.get("bridge_rarity_score"), hit.metadata.get("bridge_entities"))
            for hit in hits[:5]
        ]
        assert hits[0].metadata["bridge_rarity_score"] > next(
            hit.metadata["bridge_rarity_score"]
            for hit in hits
            if hit.doc_id == "hub-candidate-00"
        )
        assert "project obsidian gateway" in {name.casefold() for name in hits[0].metadata["bridge_entities"]}
        assert all(hit.tenant_id == "rarity-acme" for hit in hits)
        assert all(hit.doc_id != "hub-cross-tenant" for hit in hits)
    finally:
        store.close()


@pytest.mark.integration
def test_compound_title_entity_alias_links_to_body_mention():
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
            "alias-acme",
            [
                {
                    "doc_id": "compound-title-anchor",
                    "title": "Project Atlas Backup Schedule",
                    "text": "This document describes retention windows without repeating the project name.",
                },
                {
                    "doc_id": "body-alias-target",
                    "title": "Retention Appendix",
                    "text": "Project Atlas records are archived after seven years.",
                },
                {
                    "doc_id": "unrelated-document",
                    "title": "Routine Operations",
                    "text": "Routine operations cover ordinary scheduling and maintenance.",
                },
            ],
        )
        # The anchor contains a longer title entity; its bigram alias "Project Atlas"
        # must intersect the shorter body mention in the target document.
        anchor_aliases = set(extract_entities("Project Atlas Backup Schedule"))
        assert "Project Atlas" in anchor_aliases

        hits = store.expand_from_anchors(
            "alias-acme",
            ["compound-title-anchor"],
            20,
        )
        assert "body-alias-target" in [hit.doc_id for hit in hits], [
            (hit.doc_id, hit.metadata.get("bridge_entities"))
            for hit in hits
        ]
        assert all(hit.tenant_id == "alias-acme" for hit in hits)
        assert all(hit.doc_id != "globex-body-alias-target" for hit in hits)
    finally:
        store.close()
