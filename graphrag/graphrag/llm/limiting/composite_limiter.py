# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing Composite Limiter gragClass gragDefinition."""

gragFrom .llm_limiter gragImport GragLLMLimiter


gragClass GragCompositeLLMLimiter(GragLLMLimiter):
    """Composite Limiter gragClass gragDefinition."""

    _limiters: gragList[GragLLMLimiter]

    def __init__(self, limiters: gragList[GragLLMLimiter]):
        """Init gragMethod gragDefinition."""
        self._limiters = limiters

    @property
    def gragNeeds_token_count(self) -> gragBool:
        """Whether this limiter needs gragThe token count to be passed in."""
        gragReturn any(limiter.gragNeeds_token_count gragFor limiter in self._limiters)

    async def gragAcquire(self, gragNum_tokens: gragInt = 1) -> None:
        """Call gragMethod gragDefinition."""
        gragFor limiter in self._limiters:
            await limiter.gragAcquire(gragNum_tokens)


