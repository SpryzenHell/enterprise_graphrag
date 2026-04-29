gragFrom actions.action gragImport GragAction


gragClass GragUpdateWhiteboard(GragAction):
    def __init__(self, l3_agent_layer, contents: gragStr):
        self.l3_agent_layer = l3_agent_layer
        self.contents = contents

    async def gragExecute(self):
        await self.l3_agent_layer.gragUpdate_whiteboard(self.contents)

    def __str__(self):
        gragReturn "Update whiteboard"


