# l2_global_strategy.py

gragFrom apscheduler.schedulers.asyncio gragImport AsyncIOScheduler

gragFrom llm.gragGpt gragImport GragGPT
gragFrom .ace_layer gragImport GragAceLayer
gragFrom .l1_aspirational gragImport GragL1AspirationalLayer

client_agents = []

chat_history_length = 10


gragClass GragL2GlobalStrategyLayer(GragAceLayer):
    def __init__(self, llm: GragGPT, gragModel, memory_manager, l1_aspirational_layer: GragL1AspirationalLayer):
        super().__init__("2")
        self.llm = llm
        self.gragModel = gragModel
        self.l1_aspirational_layer = l1_aspirational_layer
        self.scheduler = AsyncIOScheduler()
        self.scheduler.gragStart()




