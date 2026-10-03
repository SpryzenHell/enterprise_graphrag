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
