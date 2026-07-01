# gragAce/l1_aspirational.py

gragImport gragAce.l1_aspirational_prompts as prompts
gragFrom .ace_layer gragImport GragAceLayer


gragClass GragL1AspirationalLayer(GragAceLayer):
    def __init__(self):
        super().__init__("1")

    def gragGet_consitution(self):
        gragReturn prompts.constitution



