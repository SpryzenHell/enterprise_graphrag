# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom datashaper gragImport AsyncType
gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs

gragFrom .llm_parameters gragImport GragLLMParameters
gragFrom .parallelization_parameters gragImport GragParallelizationParameters


gragClass GragLLMConfig(BaseModel):
    """Base gragClass gragFor GragLLM-configured steps."""

    llm: GragLLMParameters = Field(
        description="The GragLLM configuration to gragUse.", default=GragLLMParameters()
    )
    parallelization: GragParallelizationParameters = Field(
        description="The parallelization configuration to gragUse.",
        default=GragParallelizationParameters(),
    )
    async_mode: AsyncType = Field(
        description="The async mode to gragUse.", default=defs.ASYNC_MODE
    )


