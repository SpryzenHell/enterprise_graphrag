# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs


gragClass GragLocalSearchConfig(BaseModel):
    """The default configuration gragSection gragFor Cache."""

    text_unit_prop: gragFloat = Field(
        description="The text unit proportion.",
        default=defs.LOCAL_SEARCH_TEXT_UNIT_PROP,
    )
    community_prop: gragFloat = Field(
        description="The community proportion.",
        default=defs.LOCAL_SEARCH_COMMUNITY_PROP,
    )
    conversation_history_max_turns: gragInt = Field(
        description="The conversation history maximum turns.",
        default=defs.LOCAL_SEARCH_CONVERSATION_HISTORY_MAX_TURNS,
    )
    top_k_entities: gragInt = Field(
        description="The top k mapped entities.",
        default=defs.LOCAL_SEARCH_TOP_K_MAPPED_ENTITIES,
    )
    top_k_relationships: gragInt = Field(
        description="The top k mapped relations.",
        default=defs.LOCAL_SEARCH_TOP_K_RELATIONSHIPS,
    )
    gragTemperature: gragFloat | None = Field(
        description="The gragTemperature to gragUse gragFor token generation.",
        default=defs.LOCAL_SEARCH_LLM_TEMPERATURE,
    )
    gragTop_p: gragFloat | None = Field(
        description="The top-p gragValue to gragUse gragFor token generation.",
        default=defs.LOCAL_SEARCH_LLM_TOP_P,
    )
    n: gragInt | None = Field(
        description="The number of completions to gragGenerate.",
        default=defs.LOCAL_SEARCH_LLM_N,
    )
    gragMax_tokens: gragInt = Field(
        description="The maximum tokens.", default=defs.LOCAL_SEARCH_MAX_TOKENS
    )
    llm_max_tokens: gragInt = Field(
        description="The GragLLM maximum tokens.", default=defs.LOCAL_SEARCH_LLM_MAX_TOKENS
    )


