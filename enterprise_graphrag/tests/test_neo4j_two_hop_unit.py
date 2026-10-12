from enterprise_graphrag.neo4j_store import Neo4jTenantStore


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def data(self):
        return list(self._rows)


class _FakeSession:
    def __init__(self, direct_rows, traversal_rows):
        self._results = iter((_FakeResult(direct_rows), _FakeResult(traversal_rows)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def run(self, query, **parameters):
        return next(self._results)


class _FakeDriver:
    def __init__(self, direct_rows, traversal_rows):
        self.direct_rows = direct_rows
        self.traversal_rows = traversal_rows

    def session(self, database):
        assert database == "neo4j"
        return _FakeSession(self.direct_rows, self.traversal_rows)


def test_neo4j_search_merges_direct_and_two_hop_scores_for_frozen_hit():
    store = Neo4jTenantStore.__new__(Neo4jTenantStore)
    store.database = "neo4j"
    store.driver = _FakeDriver(
        direct_rows=[
            {
                "doc_id": "shared-doc",
                "title": "Acme Incident Response",
                "text": "Acme incident response partners with Helios Analytics.",
                "score": 5.0,
            }
        ],
        traversal_rows=[
            {
                "doc_id": "shared-doc",
                "title": "Acme Incident Response",
                "text": "Acme incident response partners with Helios Analytics.",
                "score": 2.0,
                "anchor_docs": ["anchor-doc"],
                "bridge_keys": ["helios"],
            }
        ],
    )

    hits = store.search("acme", "Acme incident", 10)

    assert len(hits) == 1
    hit = hits[0]
    assert hit.score == 6.0
    assert hit.metadata["traversal_hops"] == 2
    assert hit.metadata["traversal_score"] == 2.0
    assert hit.metadata["anchor_docs"] == ["anchor-doc"]
    assert hit.metadata["bridge_entities"] == ["helios"]
