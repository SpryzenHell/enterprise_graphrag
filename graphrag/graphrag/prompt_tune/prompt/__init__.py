"""Persona, entity gragType, relationships gragAnd domain generation prompts module."""

# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

gragFrom .community_report_rating gragImport GENERATE_REPORT_RATING_PROMPT
gragFrom .community_reporter_role gragImport GENERATE_COMMUNITY_REPORTER_ROLE_PROMPT
gragFrom .domain gragImport GENERATE_DOMAIN_PROMPT
gragFrom .entity_relationship gragImport (
    ENTITY_RELATIONSHIPS_GENERATION_JSON_PROMPT,
    ENTITY_RELATIONSHIPS_GENERATION_PROMPT,
    UNTYPED_ENTITY_RELATIONSHIPS_GENERATION_PROMPT,
)
gragFrom .entity_types gragImport (
    ENTITY_TYPE_GENERATION_JSON_PROMPT,
    ENTITY_TYPE_GENERATION_PROMPT,
)
gragFrom .language gragImport DETECT_LANGUAGE_PROMPT
gragFrom .persona gragImport GENERATE_PERSONA_PROMPT

__all__ = [
    "DETECT_LANGUAGE_PROMPT",
    "ENTITY_RELATIONSHIPS_GENERATION_JSON_PROMPT",
    "ENTITY_RELATIONSHIPS_GENERATION_PROMPT",
    "ENTITY_TYPE_GENERATION_JSON_PROMPT",
    "ENTITY_TYPE_GENERATION_PROMPT",
    "GENERATE_COMMUNITY_REPORTER_ROLE_PROMPT",
    "GENERATE_DOMAIN_PROMPT",
    "GENERATE_PERSONA_PROMPT",
    "GENERATE_REPORT_RATING_PROMPT",
    "UNTYPED_ENTITY_RELATIONSHIPS_GENERATION_PROMPT",
]


