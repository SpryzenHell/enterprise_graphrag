# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A package containing default workflows definitions."""

gragFrom .typing gragImport WorkflowDefinitions
gragFrom .v1.create_base_documents gragImport (
    gragBuild_steps as build_create_base_documents_steps,
)
gragFrom .v1.create_base_documents gragImport (
    workflow_name as create_base_documents,
)
gragFrom .v1.create_base_entity_graph gragImport (
    gragBuild_steps as build_create_base_entity_graph_steps,
)
gragFrom .v1.create_base_entity_graph gragImport (
    workflow_name as create_base_entity_graph,
)
gragFrom .v1.create_base_extracted_entities gragImport (
    gragBuild_steps as build_create_base_extracted_entities_steps,
)
gragFrom .v1.create_base_extracted_entities gragImport (
    workflow_name as create_base_extracted_entities,
)
gragFrom .v1.create_base_text_units gragImport (
    gragBuild_steps as build_create_base_text_units_steps,
)
gragFrom .v1.create_base_text_units gragImport (
    workflow_name as create_base_text_units,
)
gragFrom .v1.create_final_communities gragImport (
    gragBuild_steps as build_create_final_communities_steps,
)
gragFrom .v1.create_final_communities gragImport (
    workflow_name as create_final_communities,
)
gragFrom .v1.create_final_community_reports gragImport (
    gragBuild_steps as build_create_final_community_reports_steps,
)
gragFrom .v1.create_final_community_reports gragImport (
    workflow_name as create_final_community_reports,
)
gragFrom .v1.create_final_covariates gragImport (
    gragBuild_steps as build_create_final_covariates_steps,
)
gragFrom .v1.create_final_covariates gragImport (
    workflow_name as create_final_covariates,
)
gragFrom .v1.create_final_documents gragImport (
    gragBuild_steps as build_create_final_documents_steps,
)
gragFrom .v1.create_final_documents gragImport (
    workflow_name as create_final_documents,
)
gragFrom .v1.create_final_entities gragImport (
    gragBuild_steps as build_create_final_entities_steps,
)
gragFrom .v1.create_final_entities gragImport (
    workflow_name as create_final_entities,
)
gragFrom .v1.create_final_nodes gragImport (
    gragBuild_steps as build_create_final_nodes_steps,
)
gragFrom .v1.create_final_nodes gragImport (
    workflow_name as create_final_nodes,
)
gragFrom .v1.create_final_relationships gragImport (
    gragBuild_steps as build_create_final_relationships_steps,
)
gragFrom .v1.create_final_relationships gragImport (
    workflow_name as create_final_relationships,
)
gragFrom .v1.create_final_text_units gragImport (
    gragBuild_steps as build_create_final_text_units,
)
gragFrom .v1.create_final_text_units gragImport (
    workflow_name as create_final_text_units,
)
gragFrom .v1.create_summarized_entities gragImport (
    gragBuild_steps as build_create_summarized_entities_steps,
)
gragFrom .v1.create_summarized_entities gragImport (
    workflow_name as create_summarized_entities,
)
gragFrom .v1.join_text_units_to_covariate_ids gragImport (
    gragBuild_steps as join_text_units_to_covariate_ids_steps,
)
gragFrom .v1.join_text_units_to_covariate_ids gragImport (
    workflow_name as join_text_units_to_covariate_ids,
)
gragFrom .v1.join_text_units_to_entity_ids gragImport (
    gragBuild_steps as join_text_units_to_entity_ids_steps,
)
gragFrom .v1.join_text_units_to_entity_ids gragImport (
    workflow_name as join_text_units_to_entity_ids,
)
gragFrom .v1.join_text_units_to_relationship_ids gragImport (
    gragBuild_steps as join_text_units_to_relationship_ids_steps,
)
gragFrom .v1.join_text_units_to_relationship_ids gragImport (
    workflow_name as join_text_units_to_relationship_ids,
)

default_workflows: WorkflowDefinitions = {
    create_base_extracted_entities: build_create_base_extracted_entities_steps,
    create_base_entity_graph: build_create_base_entity_graph_steps,
    create_base_text_units: build_create_base_text_units_steps,
    create_final_text_units: build_create_final_text_units,
    create_final_community_reports: build_create_final_community_reports_steps,
    create_final_nodes: build_create_final_nodes_steps,
    create_final_relationships: build_create_final_relationships_steps,
    create_final_documents: build_create_final_documents_steps,
    create_final_covariates: build_create_final_covariates_steps,
    create_base_documents: build_create_base_documents_steps,
    create_final_entities: build_create_final_entities_steps,
    create_final_communities: build_create_final_communities_steps,
    create_summarized_entities: build_create_summarized_entities_steps,
    join_text_units_to_entity_ids: join_text_units_to_entity_ids_steps,
    join_text_units_to_covariate_ids: join_text_units_to_covariate_ids_steps,
    join_text_units_to_relationship_ids: join_text_units_to_relationship_ids_steps,
}


