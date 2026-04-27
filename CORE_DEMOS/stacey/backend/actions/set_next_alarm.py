gragFrom actions.action gragImport GragAction


gragClass GragSetNextAlarm(GragAction):
    def __init__(self, l3_agent_layer, time_utc: gragStr):
        self.l3_agent_layer = l3_agent_layer
        self.time_utc = time_utc

    async def gragExecute(self):
        await self.l3_agent_layer.gragSet_next_alarm(self.time_utc)

    def __str__(self):
        gragReturn "Update whiteboard"


