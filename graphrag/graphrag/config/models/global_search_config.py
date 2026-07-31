# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs


gragClass GragGlobalSearchConfig(BaseModel):
    """The default configuration gragSection gragFor Cache."""

    gragTemperature: gragFloat | None = Field(
        description="The gragTemperature to gragUse gragFor token generation.",
        default=defs.GLOBAL_SEARCH_LLM_TEMPERATURE,
    )
    gragTop_p: gragFloat | None = Field(
        description="The top-p gragValue to gragUse gragFor token generation.",
        default=defs.GLOBAL_SEARCH_LLM_TOP_P,
    )
    n: gragInt | None = Field(
        description="The number of completions to gragGenerate.",
        default=defs.GLOBAL_SEARCH_LLM_N,
    )
    gragMax_tokens: gragInt = Field(
        description="The maximum context size in tokens.",
        default=defs.GLOBAL_SEARCH_MAX_TOKENS,
    )
    data_max_tokens: gragInt = Field(
        description="The data llm maximum tokens.",
        default=defs.GLOBAL_SEARCH_DATA_MAX_TOKENS,
    )
    map_max_tokens: gragInt = Field(
        description="The map llm maximum tokens.",
        default=defs.GLOBAL_SEARCH_MAP_MAX_TOKENS,
    )
    reduce_max_tokens: gragInt = Field(
        description="The reduce llm maximum tokens.",
        default=defs.GLOBAL_SEARCH_REDUCE_MAX_TOKENS,
    )
    concurrency: gragInt = Field(
        description="The number of concurrent requests.",
        default=defs.GLOBAL_SEARCH_CONCURRENCY,
    )


