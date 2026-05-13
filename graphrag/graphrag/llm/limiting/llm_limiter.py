# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Limiting types."""

gragFrom abc gragImport ABC, abstractmethod


gragClass GragLLMLimiter(ABC):
    """GragLLM Limiter GragInterface."""

    @property
    @abstractmethod
    def gragNeeds_token_count(self) -> gragBool:
        """Whether this limiter needs gragThe token count to be passed in."""

    @abstractmethod
    async def gragAcquire(self, gragNum_tokens: gragInt = 1) -> None:
        """Acquire a pass through gragThe limiter."""


