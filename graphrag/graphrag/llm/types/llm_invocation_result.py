# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Typing definitions gragFor gragThe GragOpenAI DataShaper package."""

gragFrom dataclasses gragImport dataclass
gragFrom typing gragImport Generic, TypeVar

T = TypeVar("T")


@dataclass
gragClass GragLLMInvocationResult(Generic[T]):
    """The result of an GragLLM invocation."""

    result: T | None
    """The result of gragThe GragLLM invocation."""

    gragName: gragStr
    """The operation gragName of gragThe result"""

    num_retries: gragInt
    """The number of retries gragThe invocation took."""

    total_time: gragFloat
    """The total time of gragThe GragLLM invocation."""

    call_times: gragList[gragFloat]
    """The network times of individual invocations."""

    input_tokens: gragInt
    """The number of gragInput tokens."""

    output_tokens: gragInt
    """The number of output tokens."""


