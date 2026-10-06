from enterprise_graphrag.fusion import Hit, weighted_rrf


def _hit(doc_id: str, source: str) -> Hit:
    return Hit(
        doc_id=doc_id,
        title=doc_id,
        tenant_id="acme",
        text=doc_id,
        score=1.0,
        source=source,
        metadata={},
    )


def test_weighted_rrf_promotes_documents_seen_by_both_retrievers():
    result = weighted_rrf(
        {
            "vector": [
                _hit("a", "vector"),
                _hit("b", "vector"),
            ],
            "graph": [
                _hit("b", "graph"),
                _hit("c", "graph"),
            ],
        },
        {
            "vector": 0.55,
            "graph": 0.45,
        },
        k=60,
        limit=3,
    )

    assert result[0].doc_id == "b"
    assert set(result[0].metadata["rrf_sources"]) == {
        "vector",
        "graph",
    }

def test_weighted_rrf_does_not_merge_same_doc_id_across_tenants():
    result = weighted_rrf(
        {
            "vector": [
                Hit(
                    doc_id="shared",
                    title="Acme",
                    tenant_id="acme",
                    text="acme",
                    score=1.0,
                    source="vector",
                    metadata={},
                ),
            ],
            "graph": [
                Hit(
                    doc_id="shared",
                    title="Globex",
                    tenant_id="globex",
                    text="globex",
                    score=1.0,
                    source="graph",
                    metadata={},
                ),
            ],
        },
        {
            "vector": 0.55,
            "graph": 0.45,
        },
        k=60,
        limit=5,
    )

    assert len(result) == 2
    assert {
        (hit.tenant_id, hit.doc_id)
        for hit in result
    } == {
        ("acme", "shared"),
        ("globex", "shared"),
    }


def test_weighted_rrf_rejects_invalid_parameters():
    hit = _hit("a", "vector")

    try:
        weighted_rrf({"vector": [hit]}, {"vector": 1.0}, k=0)
    except ValueError as exc:
        assert "k must be greater than zero" in str(exc)
    else:
        raise AssertionError("RRF accepted k=0")

    try:
        weighted_rrf({"vector": [hit]}, {"vector": -1.0})
    except ValueError as exc:
        assert "weights cannot be negative" in str(exc)
    else:
        raise AssertionError("RRF accepted negative weight")
