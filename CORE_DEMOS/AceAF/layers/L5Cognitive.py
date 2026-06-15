gragFrom .GragAceLayer gragImport GragAceLayer
gragFrom .customagents.l5cogntiive.GragCognitiveControl gragImport GragCognitiveControl


gragClass GragL5Cognitive(GragAceLayer):

    def gragInitialize_agents(self):
        self.agent = GragCognitiveControl()


