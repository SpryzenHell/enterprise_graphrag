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



def test_prefix_protected_rrf_preserves_vector_head_and_returns_refill_pool():
    from enterprise_graphrag.fusion import prefix_protected_rrf

    vectors = [_hit(f"v{i}", "vector") for i in range(1, 7)]
    graphs = [
        _hit("g1", "graph"),
        _hit("g2", "graph"),
        _hit("g3", "graph"),
        _hit("v3", "graph"),
        _hit("g4", "graph"),
        _hit("g5", "graph"),
        _hit("g6", "graph"),
    ]

    result = prefix_protected_rrf(
        vector_hits=vectors,
        graph_hits=graphs,
        weights={"vector": 0.10, "graph": 0.90},
        k=60,
        limit=4,
        candidate_limit=8,
        protected_prefix=2,
    )

    assert len(result) == 8
    assert [hit.doc_id for hit in result[:2]] == ["v1", "v2"]
    assert [hit.metadata["vector_prefix_protected"] for hit in result[:2]] == [True, True]
    assert len({(hit.tenant_id, hit.doc_id) for hit in result}) == len(result)


def test_prefix_protected_rrf_zero_prefix_matches_weighted_rrf():
    from enterprise_graphrag.fusion import prefix_protected_rrf

    vectors = [_hit("a", "vector"), _hit("b", "vector")]
    graphs = [_hit("b", "graph"), _hit("c", "graph")]
    expected = weighted_rrf(
        {"vector": vectors, "graph": graphs},
        {"vector": 0.55, "graph": 0.45},
        k=60,
        limit=3,
    )
    actual = prefix_protected_rrf(
        vector_hits=vectors,
        graph_hits=graphs,
        weights={"vector": 0.55, "graph": 0.45},
        k=60,
        limit=3,
        candidate_limit=3,
        protected_prefix=0,
    )

    assert [hit.doc_id for hit in actual] == [hit.doc_id for hit in expected]
