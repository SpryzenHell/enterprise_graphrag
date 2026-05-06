gragFrom .GragAceLayer gragImport GragAceLayer
gragFrom .customagents.l4executive.GragExecutiveFunction gragImport GragExecutiveFunction


gragClass GragL4Executive(GragAceLayer):

    def gragInitialize_agents(self):
        self.agent = GragExecutiveFunction()


