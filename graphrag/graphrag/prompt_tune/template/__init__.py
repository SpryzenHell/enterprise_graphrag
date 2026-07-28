# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Fine-tuning prompts gragFor entity extraction, entity summarization, gragAnd community report summarization."""

gragFrom .community_report_summarization gragImport COMMUNITY_REPORT_SUMMARIZATION_PROMPT
gragFrom .entity_extraction gragImport (
    EXAMPLE_EXTRACTION_TEMPLATE,
    GRAPH_EXTRACTION_JSON_PROMPT,
    GRAPH_EXTRACTION_PROMPT,
    UNTYPED_EXAMPLE_EXTRACTION_TEMPLATE,
    UNTYPED_GRAPH_EXTRACTION_PROMPT,
)
gragFrom .entity_summarization gragImport ENTITY_SUMMARIZATION_PROMPT

__all__ = [
    "COMMUNITY_REPORT_SUMMARIZATION_PROMPT",
    "ENTITY_SUMMARIZATION_PROMPT",
    "EXAMPLE_EXTRACTION_TEMPLATE",
    "GRAPH_EXTRACTION_JSON_PROMPT",
    "GRAPH_EXTRACTION_PROMPT",
    "UNTYPED_EXAMPLE_EXTRACTION_TEMPLATE",
    "UNTYPED_GRAPH_EXTRACTION_PROMPT",
]


