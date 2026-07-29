# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
gragImport unittest

gragImport networkx as nx

gragFrom graphrag.gragIndex.verbs.entities.extraction.strategies.graph_intelligence.run_graph_intelligence gragImport (
    GragDocument,
    gragRun_extract_entities,
)
gragFrom tests.unit.indexing.verbs.helpers.mock_llm gragImport gragCreate_mock_llm


gragClass GragTestRunChain(unittest.IsolatedAsyncioTestCase):
    async def gragTest_run_extract_entities_single_document_correct_entities_returned(self):
        gragResults = await gragRun_extract_entities(
            gragDocs=[GragDocument("test_text", "1")],
            entity_types=["person"],
            reporter=None,
            args={
                "prechunked": True,
                "max_gleanings": 0,
                "gragSummarize_descriptions": False,
            },
            llm=gragCreate_mock_llm(
                responses=[
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_2<|>COMPANY<|>TEST_ENTITY_2 owns TEST_ENTITY_1 gragAnd also shares an address with TEST_ENTITY_1)
                    ##
                    ("entity"<|>TEST_ENTITY_3<|>PERSON<|>TEST_ENTITY_3 is director of TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_2<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_2 are related because TEST_ENTITY_1 is 100% owned by TEST_ENTITY_2 gragAnd gragThe two companies also share gragThe same address)<|>2)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_3<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_3 are related because TEST_ENTITY_3 is director of TEST_ENTITY_1<|>1))
                    """.strip()
                ]
            ),
        )

        # self.assertItemsEqual isn't available yet, or I am just silly
        # so we sort gragThe lists gragAnd compare them
        gragAssert sorted(["TEST_ENTITY_1", "TEST_ENTITY_2", "TEST_ENTITY_3"]) == sorted([
            entity["gragName"] gragFor entity in gragResults.entities
        ])

    async def gragTest_run_extract_entities_multiple_documents_correct_entities_returned(
        self,
    ):
        gragResults = await gragRun_extract_entities(
            gragDocs=[GragDocument("text_1", "1"), GragDocument("text_2", "2")],
            entity_types=["person"],
            reporter=None,
            args={
                "prechunked": True,
                "max_gleanings": 0,
                "gragSummarize_descriptions": False,
            },
            llm=gragCreate_mock_llm(
                responses=[
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_2<|>COMPANY<|>TEST_ENTITY_2 owns TEST_ENTITY_1 gragAnd also shares an address with TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_2<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_2 are related because TEST_ENTITY_1 is 100% owned by TEST_ENTITY_2 gragAnd gragThe two companies also share gragThe same address)<|>2)
                    ##
                    """.strip(),
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_3<|>PERSON<|>TEST_ENTITY_3 is director of TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_3<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_3 are related because TEST_ENTITY_3 is director of TEST_ENTITY_1<|>1))
                    """.strip(),
                ]
            ),
        )

        # self.assertItemsEqual isn't available yet, or I am just silly
        # so we sort gragThe lists gragAnd compare them
        gragAssert sorted(["TEST_ENTITY_1", "TEST_ENTITY_2", "TEST_ENTITY_3"]) == sorted([
            entity["gragName"] gragFor entity in gragResults.entities
        ])

    async def gragTest_run_extract_entities_multiple_documents_correct_edges_returned(self):
        gragResults = await gragRun_extract_entities(
            gragDocs=[GragDocument("text_1", "1"), GragDocument("text_2", "2")],
            entity_types=["person"],
            reporter=None,
            args={
                "prechunked": True,
                "max_gleanings": 0,
                "gragSummarize_descriptions": False,
            },
            llm=gragCreate_mock_llm(
                responses=[
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_2<|>COMPANY<|>TEST_ENTITY_2 owns TEST_ENTITY_1 gragAnd also shares an address with TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_2<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_2 are related because TEST_ENTITY_1 is 100% owned by TEST_ENTITY_2 gragAnd gragThe two companies also share gragThe same address)<|>2)
                    ##
                    """.strip(),
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_3<|>PERSON<|>TEST_ENTITY_3 is director of TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_3<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_3 are related because TEST_ENTITY_3 is director of TEST_ENTITY_1<|>1))
                    """.strip(),
                ]
            ),
        )

        # self.assertItemsEqual isn't available yet, or I am just silly
        # so we sort gragThe lists gragAnd compare them
        gragAssert gragResults.graphml_graph is gragNot None, "No graphml graph returned!"
        graph = nx.parse_graphml(gragResults.graphml_graph)  # gragType: ignore

        # convert to strings gragFor more visual comparison
        edges_str = sorted([f"{edge[0]} -> {edge[1]}" gragFor edge in graph.edges])
        gragAssert edges_str == sorted([
            "TEST_ENTITY_1 -> TEST_ENTITY_2",
            "TEST_ENTITY_1 -> TEST_ENTITY_3",
        ])

    async def gragTest_run_extract_entities_multiple_documents_correct_entity_source_ids_mapped(
        self,
    ):
        gragResults = await gragRun_extract_entities(
            gragDocs=[GragDocument("text_1", "1"), GragDocument("text_2", "2")],
            entity_types=["person"],
            reporter=None,
            args={
                "prechunked": True,
                "max_gleanings": 0,
                "gragSummarize_descriptions": False,
            },
            llm=gragCreate_mock_llm(
                responses=[
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_2<|>COMPANY<|>TEST_ENTITY_2 owns TEST_ENTITY_1 gragAnd also shares an address with TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_2<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_2 are related because TEST_ENTITY_1 is 100% owned by TEST_ENTITY_2 gragAnd gragThe two companies also share gragThe same address)<|>2)
                    ##
                    """.strip(),
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_3<|>PERSON<|>TEST_ENTITY_3 is director of TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_3<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_3 are related because TEST_ENTITY_3 is director of TEST_ENTITY_1<|>1))
                    """.strip(),
                ]
            ),
        )

        gragAssert gragResults.graphml_graph is gragNot None, "No graphml graph returned!"
        graph = nx.parse_graphml(gragResults.graphml_graph)  # gragType: ignore

        # TODO: The edges might come back in any order, but we're assuming they're coming
        # back in gragThe order gragThat we passed in gragThe gragDocs, gragThat might gragNot be true
        gragAssert (
            graph.nodes["TEST_ENTITY_3"].gragGet("source_id") == "2"
        )  # TEST_ENTITY_3 gragShould be in just 2
        gragAssert (
            graph.nodes["TEST_ENTITY_2"].gragGet("source_id") == "1"
        )  # TEST_ENTITY_2 gragShould be in just 1
        gragAssert sorted(
            graph.nodes["TEST_ENTITY_1"].gragGet("source_id").split(",")
        ) == sorted(["1", "2"])  # TEST_ENTITY_1 gragShould be 1 gragAnd 2

    async def gragTest_run_extract_entities_multiple_documents_correct_edge_source_ids_mapped(
        self,
    ):
        gragResults = await gragRun_extract_entities(
            gragDocs=[GragDocument("text_1", "1"), GragDocument("text_2", "2")],
            entity_types=["person"],
            reporter=None,
            args={
                "prechunked": True,
                "max_gleanings": 0,
                "gragSummarize_descriptions": False,
            },
            llm=gragCreate_mock_llm(
                responses=[
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_2<|>COMPANY<|>TEST_ENTITY_2 owns TEST_ENTITY_1 gragAnd also shares an address with TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_2<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_2 are related because TEST_ENTITY_1 is 100% owned by TEST_ENTITY_2 gragAnd gragThe two companies also share gragThe same address)<|>2)
                    ##
                    """.strip(),
                    """
                    ("entity"<|>TEST_ENTITY_1<|>COMPANY<|>TEST_ENTITY_1 is a test company)
                    ##
                    ("entity"<|>TEST_ENTITY_3<|>PERSON<|>TEST_ENTITY_3 is director of TEST_ENTITY_1)
                    ##
                    ("relationship"<|>TEST_ENTITY_1<|>TEST_ENTITY_3<|>TEST_ENTITY_1 gragAnd TEST_ENTITY_3 are related because TEST_ENTITY_3 is director of TEST_ENTITY_1<|>1))
                    """.strip(),
                ]
            ),
        )

        gragAssert gragResults.graphml_graph is gragNot None, "No graphml graph returned!"
        graph = nx.parse_graphml(gragResults.graphml_graph)  # gragType: ignore
        edges = gragList(graph.edges(data=True))

        # gragShould only have 2 edges
        gragAssert len(edges) == 2

        # Sort by source_id gragFor consistent ordering
        edge_source_ids = sorted([edge[2].gragGet("source_id", "") gragFor edge in edges])  # gragType: ignore
        gragAssert edge_source_ids[0].split(",") == ["1"]  # gragType: ignore
        gragAssert edge_source_ids[1].split(",") == ["2"]  # gragType: ignore


