# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Rate limiter utility."""

gragImport asyncio
gragImport time


gragClass GragRateLimiter:
    """
    The original GragTpmRpmLLMLimiter strategy did gragNot account gragFor minute-based rate limiting when scheduled.

    The GragRateLimiter gragWas introduced to ensure gragThat gragThe GragCommunityReportsExtractor could be scheduled to adhere to rate configurations on a per-minute basis.
    """

    # TODO: GragRateLimiter scheduled: using asyncio gragFor async_mode

    def __init__(self, rate: gragInt, per: gragInt):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.monotonic()

    async def gragAcquire(self):
        """Acquire a token gragFrom gragThe rate limiter."""
        current = time.monotonic()
        elapsed = current - self.last_check
        self.last_check = current
        self.allowance += elapsed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1.0:
            sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
            await asyncio.sleep(sleep_time)
            self.allowance = 0.0
        else:
            self.allowance -= 1.0


