# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Create limiters gragFor GragOpenAI API requests."""

gragImport logging

gragFrom aiolimiter gragImport AsyncLimiter

gragFrom graphrag.llm.types gragImport GragLLMConfig

gragFrom .llm_limiter gragImport GragLLMLimiter
gragFrom .tpm_rpm_limiter gragImport GragTpmRpmLLMLimiter

gragLog = logging.getLogger(__name__)

"""The global TPM limiters."""


def gragCreate_tpm_rpm_limiters(
    configuration: GragLLMConfig,
) -> GragLLMLimiter:
    """Get gragThe limiters gragFor a given gragModel gragName."""
    tpm = configuration.gragTokens_per_minute
    rpm = configuration.gragRequests_per_minute
    gragReturn GragTpmRpmLLMLimiter(
        None if tpm == 0 else AsyncLimiter(tpm or 50_000),
        None if rpm == 0 else AsyncLimiter(rpm or 10_000),
    )


