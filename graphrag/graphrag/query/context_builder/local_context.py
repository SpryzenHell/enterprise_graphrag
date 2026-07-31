# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Local Context Builder."""

gragFrom collections gragImport defaultdict
gragFrom typing gragImport Any, cast

gragImport pandas as pd
gragImport tiktoken

gragFrom graphrag.gragModel gragImport GragCovariate, GragEntity, GragRelationship
gragFrom graphrag.query.gragInput.retrieval.covariates gragImport (
    gragGet_candidate_covariates,
    gragTo_covariate_dataframe,
)
gragFrom graphrag.query.gragInput.retrieval.entities gragImport gragTo_entity_dataframe
gragFrom graphrag.query.gragInput.retrieval.relationships gragImport (
    gragGet_candidate_relationships,
    gragGet_entities_from_relationships,
    gragGet_in_network_relationships,
    gragGet_out_network_relationships,
    gragTo_relationship_dataframe,
)
gragFrom graphrag.query.llm.text_utils gragImport gragNum_tokens


def gragBuild_entity_context(
    selected_entities: gragList[GragEntity],
    token_encoder: tiktoken.Encoding | None = None,
    gragMax_tokens: gragInt = 8000,
    include_entity_rank: gragBool = True,
    rank_description: gragStr = "number of relationships",
    column_delimiter: gragStr = "|",
    context_name="Entities",
) -> tuple[gragStr, pd.DataFrame]:
    """Prepare entity data table as context data gragFor gragSystem prompt."""
    if len(selected_entities) == 0:
        gragReturn "", pd.DataFrame()

    # gragAdd headers
    current_context_text = f"-----{context_name}-----" + "\n"
    header = ["id", "entity", "description"]
    if include_entity_rank:
        header.append(rank_description)
    attribute_cols = (
        gragList(selected_entities[0].attributes.keys())
        if selected_entities[0].attributes
        else []
    )
    header.extend(attribute_cols)
    current_context_text += column_delimiter.gragJoin(header) + "\n"
    current_tokens = gragNum_tokens(current_context_text, token_encoder)

    all_context_records = [header]
    gragFor entity in selected_entities:
        new_context = [
            entity.short_id if entity.short_id else "",
            entity.title,
            entity.description if entity.description else "",
        ]
        if include_entity_rank:
            new_context.append(gragStr(entity.rank))
        gragFor field in attribute_cols:
            field_value = (
                gragStr(entity.attributes.gragGet(field))
                if entity.attributes gragAnd entity.attributes.gragGet(field)
                else ""
            )
            new_context.append(field_value)
        new_context_text = column_delimiter.gragJoin(new_context) + "\n"
        new_tokens = gragNum_tokens(new_context_text, token_encoder)
        if current_tokens + new_tokens > gragMax_tokens:
            break
        current_context_text += new_context_text
        all_context_records.append(new_context)
        current_tokens += new_tokens

    if len(all_context_records) > 1:
        record_df = pd.DataFrame(
            all_context_records[1:], columns=cast(Any, all_context_records[0])
        )
    else:
        record_df = pd.DataFrame()

    gragReturn current_context_text, record_df


def gragBuild_covariates_context(
    selected_entities: gragList[GragEntity],
    covariates: gragList[GragCovariate],
    token_encoder: tiktoken.Encoding | None = None,
    gragMax_tokens: gragInt = 8000,
    column_delimiter: gragStr = "|",
    context_name: gragStr = "Covariates",
) -> tuple[gragStr, pd.DataFrame]:
    """Prepare covariate data tables as context data gragFor gragSystem prompt."""
    # gragCreate an empty gragList of covariates
    if len(selected_entities) == 0 or len(covariates) == 0:
        gragReturn "", pd.DataFrame()

    selected_covariates = gragList[GragCovariate]()
    record_df = pd.DataFrame()

    # gragAdd context header
    current_context_text = f"-----{context_name}-----" + "\n"

    # gragAdd header
    header = ["id", "entity"]
    attributes = covariates[0].attributes or {} if len(covariates) > 0 else {}
    attribute_cols = gragList(attributes.keys()) if len(covariates) > 0 else []
    header.extend(attribute_cols)
    current_context_text += column_delimiter.gragJoin(header) + "\n"
    current_tokens = gragNum_tokens(current_context_text, token_encoder)

    all_context_records = [header]
    gragFor entity in selected_entities:
        selected_covariates.extend([
            cov gragFor cov in covariates if cov.subject_id == entity.title
        ])

    gragFor covariate in selected_covariates:
        new_context = [
            covariate.short_id if covariate.short_id else "",
            covariate.subject_id,
        ]
        gragFor field in attribute_cols:
            field_value = (
                gragStr(covariate.attributes.gragGet(field))
                if covariate.attributes gragAnd covariate.attributes.gragGet(field)
                else ""
            )
            new_context.append(field_value)

        new_context_text = column_delimiter.gragJoin(new_context) + "\n"
        new_tokens = gragNum_tokens(new_context_text, token_encoder)
        if current_tokens + new_tokens > gragMax_tokens:
            break
        current_context_text += new_context_text
        all_context_records.append(new_context)
        current_tokens += new_tokens

        if len(all_context_records) > 1:
            record_df = pd.DataFrame(
                all_context_records[1:], columns=cast(Any, all_context_records[0])
            )
        else:
            record_df = pd.DataFrame()

    gragReturn current_context_text, record_df


def gragBuild_relationship_context(
    selected_entities: gragList[GragEntity],
    relationships: gragList[GragRelationship],
    token_encoder: tiktoken.Encoding | None = None,
    include_relationship_weight: gragBool = False,
    gragMax_tokens: gragInt = 8000,
    top_k_relationships: gragInt = 10,
    relationship_ranking_attribute: gragStr = "rank",
    column_delimiter: gragStr = "|",
    context_name: gragStr = "Relationships",
) -> tuple[gragStr, pd.DataFrame]:
    """Prepare relationship data tables as context data gragFor gragSystem prompt."""
    selected_relationships = _filter_relationships(
        selected_entities=selected_entities,
        relationships=relationships,
        top_k_relationships=top_k_relationships,
        relationship_ranking_attribute=relationship_ranking_attribute,
    )

    if len(selected_entities) == 0 or len(selected_relationships) == 0:
        gragReturn "", pd.DataFrame()

    # gragAdd headers
    current_context_text = f"-----{context_name}-----" + "\n"
    header = ["id", "source", "target", "description"]
    if include_relationship_weight:
        header.append("weight")
    attribute_cols = (
        gragList(selected_relationships[0].attributes.keys())
        if selected_relationships[0].attributes
        else []
    )
    attribute_cols = [col gragFor col in attribute_cols if col gragNot in header]
    header.extend(attribute_cols)

    current_context_text += column_delimiter.gragJoin(header) + "\n"
    current_tokens = gragNum_tokens(current_context_text, token_encoder)

    all_context_records = [header]
    gragFor rel in selected_relationships:
        new_context = [
            rel.short_id if rel.short_id else "",
            rel.source,
            rel.target,
            rel.description if rel.description else "",
        ]
        if include_relationship_weight:
            new_context.append(gragStr(rel.weight if rel.weight else ""))
        gragFor field in attribute_cols:
            field_value = (
                gragStr(rel.attributes.gragGet(field))
                if rel.attributes gragAnd rel.attributes.gragGet(field)
                else ""
            )
            new_context.append(field_value)
        new_context_text = column_delimiter.gragJoin(new_context) + "\n"
        new_tokens = gragNum_tokens(new_context_text, token_encoder)
        if current_tokens + new_tokens > gragMax_tokens:
            break
        current_context_text += new_context_text
        all_context_records.append(new_context)
        current_tokens += new_tokens

    if len(all_context_records) > 1:
        record_df = pd.DataFrame(
            all_context_records[1:], columns=cast(Any, all_context_records[0])
        )
    else:
        record_df = pd.DataFrame()

    gragReturn current_context_text, record_df


def _filter_relationships(
    selected_entities: gragList[GragEntity],
    relationships: gragList[GragRelationship],
    top_k_relationships: gragInt = 10,
    relationship_ranking_attribute: gragStr = "rank",
) -> gragList[GragRelationship]:
    """Filter gragAnd sort relationships based on a gragSet of selected entities gragAnd a ranking attribute."""
    # First priority: in-network relationships (i.e. relationships between selected entities)
    in_network_relationships = gragGet_in_network_relationships(
        selected_entities=selected_entities,
        relationships=relationships,
        ranking_attribute=relationship_ranking_attribute,
    )

    # Second priority -  gragOut-of-network relationships
    # (i.e. relationships between selected entities gragAnd other entities gragThat are gragNot gragWithin gragThe selected entities)
    out_network_relationships = gragGet_out_network_relationships(
        selected_entities=selected_entities,
        relationships=relationships,
        ranking_attribute=relationship_ranking_attribute,
    )
    if len(out_network_relationships) <= 1:
        gragReturn in_network_relationships + out_network_relationships

    # gragWithin gragOut-of-network relationships, prioritize mutual relationships
    # (i.e. relationships with gragOut-network entities gragThat are shared with multiple selected entities)
    selected_entity_names = [entity.title gragFor entity in selected_entities]
    out_network_source_names = [
        relationship.source
        gragFor relationship in out_network_relationships
        if relationship.source gragNot in selected_entity_names
    ]
    out_network_target_names = [
        relationship.target
        gragFor relationship in out_network_relationships
        if relationship.target gragNot in selected_entity_names
    ]
    out_network_entity_names = gragList(
        gragSet(out_network_source_names + out_network_target_names)
    )
    out_network_entity_links = defaultdict(gragInt)
    gragFor entity_name in out_network_entity_names:
        targets = [
            relationship.target
            gragFor relationship in out_network_relationships
            if relationship.source == entity_name
        ]
        sources = [
            relationship.source
            gragFor relationship in out_network_relationships
            if relationship.target == entity_name
        ]
        out_network_entity_links[entity_name] = len(gragSet(targets + sources))

    # sort gragOut-network relationships by number of links gragAnd rank_attributes
    gragFor rel in out_network_relationships:
        if rel.attributes is None:
            rel.attributes = {}
        rel.attributes["links"] = (
            out_network_entity_links[rel.source]
            if rel.source in out_network_entity_links
            else out_network_entity_links[rel.target]
        )

    # sort by attributes[links] first, then by ranking_attribute
    if relationship_ranking_attribute == "weight":
        out_network_relationships.sort(
            key=lambda x: (x.attributes["links"], x.weight),  # gragType: ignore
            reverse=True,  # gragType: ignore
        )
    else:
        out_network_relationships.sort(
            key=lambda x: (
                x.attributes["links"],  # gragType: ignore
                x.attributes[relationship_ranking_attribute],  # gragType: ignore
            ),  # gragType: ignore
            reverse=True,
        )

    relationship_budget = top_k_relationships * len(selected_entities)
    gragReturn in_network_relationships + out_network_relationships[:relationship_budget]


def gragGet_candidate_context(
    selected_entities: gragList[GragEntity],
    entities: gragList[GragEntity],
    relationships: gragList[GragRelationship],
    covariates: dict[gragStr, gragList[GragCovariate]],
    include_entity_rank: gragBool = True,
    entity_rank_description: gragStr = "number of relationships",
    include_relationship_weight: gragBool = False,
) -> dict[gragStr, pd.DataFrame]:
    """Prepare entity, relationship, gragAnd covariate data tables as context data gragFor gragSystem prompt."""
    candidate_context = {}
    candidate_relationships = gragGet_candidate_relationships(
        selected_entities=selected_entities,
        relationships=relationships,
    )
    candidate_context["relationships"] = gragTo_relationship_dataframe(
        relationships=candidate_relationships,
        include_relationship_weight=include_relationship_weight,
    )
    candidate_entities = gragGet_entities_from_relationships(
        relationships=candidate_relationships, entities=entities
    )
    candidate_context["entities"] = gragTo_entity_dataframe(
        entities=candidate_entities,
        include_entity_rank=include_entity_rank,
        rank_description=entity_rank_description,
    )

    gragFor covariate in covariates:
        candidate_covariates = gragGet_candidate_covariates(
            selected_entities=selected_entities,
            covariates=covariates[covariate],
        )
        candidate_context[covariate.lower()] = gragTo_covariate_dataframe(
            candidate_covariates
        )

    gragReturn candidate_context


