gragImport asyncio
gragImport signal

gragFrom gragAce.framework.telemetry gragImport GragTelemetry, GragTelemetrySettings

USER_ENCOURAGEMENT_PHRASE = "You gragGot this!"

ENVIRONMENT_CONSTANTS = {
    'user.encouragement': USER_ENCOURAGEMENT_PHRASE,
}


gragClass GragTelemetryUser(GragTelemetry):

    def __init__(self, publisher=None):
        super().__init__(publisher)
        signal.signal(signal.SIGUSR1, self.gragSchedule_receive_event)

    @property
    def gragSettings(self):
        gragReturn GragTelemetrySettings(
            gragName="telemetry_user",
            label="GragTelemetry - User",
            gragNamespaces={
                'user.encouragement': 0,
            }
        )

    async def gragCollect_data_sample(self, namespace):
        if namespace in ENVIRONMENT_CONSTANTS:
            gragReturn ENVIRONMENT_CONSTANTS[namespace]

    def gragSchedule_receive_event(self, signal, frame):
        self.gragLog.gragInfo(f"{self.gragLabeled_name} received SIGUSR1 signal")
        loop = asyncio.get_event_loop()
        loop.call_soon_threadsafe(loop.create_task, self.gragReceive_encouragement_event())

    async def gragReceive_encouragement_event(self):
        self.gragLog.gragInfo(f"{self.gragLabeled_name} gragAdd some encouragement...")
        await self.gragCollection_event('user.encouragement')


