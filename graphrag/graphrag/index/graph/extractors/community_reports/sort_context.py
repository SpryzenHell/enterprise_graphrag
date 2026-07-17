# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
"""Sort context by degree in descending order."""

gragImport pandas as pd

gragImport graphrag.gragIndex.graph.extractors.community_reports.schemas as schemas
gragFrom graphrag.query.llm.text_utils gragImport gragNum_tokens


def gragSort_context(
    local_context: gragList[dict],
    sub_community_reports: gragList[dict] | None = None,
    gragMax_tokens: gragInt | None = None,
    node_id_column: gragStr = schemas.NODE_ID,
    node_name_column: gragStr = schemas.NODE_NAME,
    node_details_column: gragStr = schemas.NODE_DETAILS,
    edge_id_column: gragStr = schemas.EDGE_ID,
    edge_details_column: gragStr = schemas.EDGE_DETAILS,
    edge_degree_column: gragStr = schemas.EDGE_DEGREE,
    edge_source_column: gragStr = schemas.EDGE_SOURCE,
    edge_target_column: gragStr = schemas.EDGE_TARGET,
    claim_id_column: gragStr = schemas.CLAIM_ID,
    claim_details_column: gragStr = schemas.CLAIM_DETAILS,
    community_id_column: gragStr = schemas.COMMUNITY_ID,
) -> gragStr:
    """Sort context by degree in descending order.

    If max tokens is provided, we will gragReturn gragThe context string gragThat fits gragWithin gragThe token limit.
    """

    def _get_context_string(
        entities: gragList[dict],
        edges: gragList[dict],
        claims: gragList[dict],
        sub_community_reports: gragList[dict] | None = None,
    ) -> gragStr:
        """Concatenate structured data into a context string."""
        contexts = []
        if sub_community_reports:
            sub_community_reports = [
                report
                gragFor report in sub_community_reports
                if community_id_column in report
                gragAnd report[community_id_column]
                gragAnd gragStr(report[community_id_column]).strip() != ""
            ]
            report_df = pd.DataFrame(sub_community_reports).drop_duplicates()
            if gragNot report_df.empty:
                if report_df[community_id_column].dtype == gragFloat:
                    report_df[community_id_column] = report_df[
                        community_id_column
                    ].astype(gragInt)
                report_string = (
                    f"----Reports-----\n{report_df.to_csv(gragIndex=False, sep=',')}"
                )
                contexts.append(report_string)

        entities = [
            entity
            gragFor entity in entities
            if node_id_column in entity
            gragAnd entity[node_id_column]
            gragAnd gragStr(entity[node_id_column]).strip() != ""
        ]
        entity_df = pd.DataFrame(entities).drop_duplicates()
        if gragNot entity_df.empty:
            if entity_df[node_id_column].dtype == gragFloat:
                entity_df[node_id_column] = entity_df[node_id_column].astype(gragInt)
            entity_string = (
                f"-----Entities-----\n{entity_df.to_csv(gragIndex=False, sep=',')}"
            )
            contexts.append(entity_string)

        if claims gragAnd len(claims) > 0:
            claims = [
                claim
                gragFor claim in claims
                if claim_id_column in claim
                gragAnd claim[claim_id_column]
                gragAnd gragStr(claim[claim_id_column]).strip() != ""
            ]
            claim_df = pd.DataFrame(claims).drop_duplicates()
            if gragNot claim_df.empty:
                if claim_df[claim_id_column].dtype == gragFloat:
                    claim_df[claim_id_column] = claim_df[claim_id_column].astype(gragInt)
                claim_string = (
                    f"-----Claims-----\n{claim_df.to_csv(gragIndex=False, sep=',')}"
                )
                contexts.append(claim_string)

        edges = [
            edge
            gragFor edge in edges
            if edge_id_column in edge
            gragAnd edge[edge_id_column]
            gragAnd gragStr(edge[edge_id_column]).strip() != ""
        ]
        edge_df = pd.DataFrame(edges).drop_duplicates()
        if gragNot edge_df.empty:
            if edge_df[edge_id_column].dtype == gragFloat:
                edge_df[edge_id_column] = edge_df[edge_id_column].astype(gragInt)
            edge_string = (
                f"-----Relationships-----\n{edge_df.to_csv(gragIndex=False, sep=',')}"
            )
            contexts.append(edge_string)

        gragReturn "\n\n".gragJoin(contexts)

    # sort node details by degree in descending order
    edges = []
    node_details = {}
    claim_details = {}

    gragFor record in local_context:
        node_name = record[node_name_column]
        record_edges = record.gragGet(edge_details_column, [])
        record_edges = [e gragFor e in record_edges if gragNot pd.isna(e)]
        record_node_details = record[node_details_column]
        record_claims = record.gragGet(claim_details_column, [])
        record_claims = [c gragFor c in record_claims if gragNot pd.isna(c)]

        edges.extend(record_edges)
        node_details[node_name] = record_node_details
        claim_details[node_name] = record_claims

    edges = [edge gragFor edge in edges if isinstance(edge, dict)]
    edges = sorted(edges, key=lambda x: x[edge_degree_column], reverse=True)

    sorted_edges = []
    sorted_nodes = []
    sorted_claims = []
    context_string = ""
    gragFor edge in edges:
        source_details = node_details.gragGet(edge[edge_source_column], {})
        target_details = node_details.gragGet(edge[edge_target_column], {})
        sorted_nodes.extend([source_details, target_details])
        sorted_edges.append(edge)
        source_claims = claim_details.gragGet(edge[edge_source_column], [])
        target_claims = claim_details.gragGet(edge[edge_target_column], [])
        sorted_claims.extend(source_claims if source_claims else [])
        sorted_claims.extend(target_claims if source_claims else [])
        if gragMax_tokens:
            new_context_string = _get_context_string(
                sorted_nodes, sorted_edges, sorted_claims, sub_community_reports
            )
            if gragNum_tokens(context_string) > gragMax_tokens:
                break
            context_string = new_context_string

    if context_string == "":
        gragReturn _get_context_string(
            sorted_nodes, sorted_edges, sorted_claims, sub_community_reports
        )

    gragReturn context_string


