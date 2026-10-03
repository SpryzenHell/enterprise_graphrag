import types

import httpx

from enterprise_graphrag.embeddings import OpenAICompatibleEmbedder
from enterprise_graphrag.errors import BackendUnavailable
from enterprise_graphrag.llm import VllmAnswerModel
from enterprise_graphrag.neo4j_store import Neo4jTenantStore
from enterprise_graphrag.security import SecurityGateway


def test_vllm_chat_contract(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": "grounded answer",
                        }
                    }
                ]
            }

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return Response()

    monkeypatch.setattr(httpx, "post", fake_post)

    model = VllmAnswerModel(
        "http://localhost:8000",
        "key",
        "served-model",
    )
    answer = model.answer(
        "What is the retention period?",
        [
            {
                "doc_id": "a1",
                "title": "Policy",
                "text": "Retention is 365 days.",
            }
        ],
    )

    assert answer == "grounded answer"
    assert captured["url"] == "http://localhost:8000/v1/chat/completions"
    assert captured["json"]["model"] == "served-model"
    assert captured["json"]["temperature"] == 0.0
    assert "Evidence:" in captured["json"]["messages"][1]["content"]


def test_vllm_prompt_logprob_ppl_contract(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "choices": [
                    {
                        "prompt_logprobs": [
                            None,
                            {"11": {"logprob": -1.0}},
                            {"12": {"logprob": -1.5}},
                        ],
                        "prompt_token_ids": [10, 11, 12]
                    }
                ]
            }

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return Response()

    monkeypatch.setattr(httpx, "post", fake_post)

    gateway = SecurityGateway(
        base_url="http://localhost:8000",
        api_key="key",
        model="served-model",
        threshold=80,
    )

    score = gateway.perplexity("hello world")

    assert score is not None
    assert captured["url"] == "http://localhost:8000/v1/completions"
    assert captured["json"]["prompt_logprobs"] == 1
    assert captured["json"]["return_token_ids"] is True


def test_neo4j_adapter_keeps_tenant_predicates(monkeypatch):
    calls = []

    class Result:
        def consume(self):
            return None

    class Session:
        def run(self, query, **params):
            calls.append((query, params))
            if "RETURN d.doc_id" in query:
                row = {
                    "doc_id": "a1",
                    "title": "Acme Policy",
                    "text": "Acme policy",
                    "score": 2.0,
                    "entity_key": "security",
                    "entity_name": "Security",
                }

                class Rows:
                    def __iter__(self):
                        return iter([row])

                return Rows()
            return Result()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class Driver:
        def session(self, database):
            calls.append(("SESSION", {"database": database}))
            return Session()

        def verify_connectivity(self):
            calls.append(("VERIFY", {}))

        def close(self):
            calls.append(("CLOSE", {}))

    fake_neo4j = types.SimpleNamespace(
        GraphDatabase=types.SimpleNamespace(
            driver=lambda *args, **kwargs: Driver()
        )
    )

    monkeypatch.setitem(
        __import__("sys").modules,
        "neo4j",
        fake_neo4j,
    )

    store = Neo4jTenantStore(
        "neo4j://localhost:7687",
        "neo4j",
        "password",
        "neo4j",
    )
    store.verify()
    store.ensure_schema()
    store.add(
        "acme",
        {
            "doc_id": "a1",
            "title": "Acme Policy",
            "text": "Acme policy",
        },
    )
    hits = store.search(
        "acme",
        "policy",
        5,
    )
    trace = store.trace(
        "acme",
        ["a1"],
    )

    assert hits[0].tenant_id == "acme"
    assert trace["nodes"]
    cypher_calls = [
        (query, params)
        for query, params in calls
        if isinstance(query, str)
    ]
    assert any(
        params.get("tenant") == "acme"
        and "tenant_id:$tenant" in query
        for query, params in cypher_calls
    )


def test_embedding_dimension_is_enforced(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "data": [
                    {
                        "index": 0,
                        "embedding": [0.1, 0.2, 0.3],
                    }
                ]
            }

    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: Response(),
    )

    model = OpenAICompatibleEmbedder(
        "http://localhost:8000",
        "key",
        "embedding-model",
        4,
    )

    try:
        model.embed(["hello"])
    except ValueError as exc:
        assert "Embedding dimension mismatch" in str(exc)
        assert "configured=4" in str(exc)
        assert "actual=3" in str(exc)
    else:
        raise AssertionError("embedding dimension mismatch was accepted")


def test_embedding_response_count_mismatch_is_rejected(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "data": [
                    {
                        "index": 0,
                        "embedding": [0.1, 0.2],
                    }
                ]
            }

    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: Response(),
    )

    model = OpenAICompatibleEmbedder(
        "http://localhost:8000",
        "key",
        "embedding-model",
        2,
    )

    try:
        model.embed(["one", "two"])
    except ValueError as exc:
        assert "count mismatch" in str(exc)
    else:
        raise AssertionError("partial embedding response was accepted")


def test_embedding_response_indexes_are_rejected_when_incomplete(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "data": [
                    {
                        "index": 0,
                        "embedding": [0.1, 0.2],
                    },
                    {
                        "index": 2,
                        "embedding": [0.3, 0.4],
                    },
                ]
            }

    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: Response(),
    )

    model = OpenAICompatibleEmbedder(
        "http://localhost:8000",
        "key",
        "embedding-model",
        2,
    )

    try:
        model.embed(["one", "two"])
    except ValueError as exc:
        assert "indexes" in str(exc)
    else:
        raise AssertionError("invalid embedding indexes were accepted")


def test_vllm_skips_generation_when_evidence_is_empty(monkeypatch):
    called = {"value": False}

    def fake_post(*args, **kwargs):
        called["value"] = True
        raise AssertionError("vLLM should not be called")

    monkeypatch.setattr(httpx, "post", fake_post)

    model = VllmAnswerModel(
        "http://localhost:8000",
        "key",
        "served-model",
    )
    assert model.answer("question", []) == "No authorized evidence found."
    assert called["value"] is False


def test_vllm_malformed_response_is_rejected(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": []}

    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: Response(),
    )

    model = VllmAnswerModel(
        "http://localhost:8000",
        "key",
        "served-model",
    )

    try:
        model.answer(
            "question",
            [
                {
                    "doc_id": "a1",
                    "title": "Policy",
                    "text": "Evidence.",
                }
            ],
        )
    except ValueError as exc:
        assert "no choices" in str(exc)
    else:
        raise AssertionError("malformed vLLM response was accepted")


def test_vllm_transport_failure_is_explicit(monkeypatch):
    def fake_post(*args, **kwargs):
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(httpx, "post", fake_post)

    model = VllmAnswerModel(
        "http://localhost:8000",
        "key",
        "served-model",
    )

    try:
        model.answer(
            "question",
            [
                {
                    "doc_id": "a1",
                    "title": "Policy",
                    "text": "Evidence.",
                }
            ],
        )
    except BackendUnavailable as exc:
        assert "vLLM answer backend is unavailable" in str(exc)
    else:
        raise AssertionError("vLLM transport failure was not surfaced")
