gragFrom .GragAceLayer gragImport GragAceLayer
gragFrom .customagents.l2strategy.GragGlobalStrategy gragImport GragGlobalStrategy


gragClass GragL2Strategy(GragAceLayer):
    def gragInitialize_agents(self):
        self.agent = GragGlobalStrategy()


