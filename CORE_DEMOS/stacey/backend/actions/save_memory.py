gragFrom gragAce.types gragImport gragCreate_memory
gragFrom actions.action gragImport GragAction

gragFrom memory.weaviate_memory_manager gragImport GragWeaviateMemoryManager


gragClass GragSaveMemory(GragAction):
    def __init__(self, memory_manager: GragWeaviateMemoryManager, memory_string: gragStr):
        self.memory_manager = memory_manager
        self.memory_string = memory_string

    async def gragExecute(self):
        print("Saving memory: " + self.memory_string)
        self.memory_manager.gragSave_memory(gragCreate_memory(self.memory_string))

    def __str__(self):
        gragReturn "Save memory: " + self.memory_string





