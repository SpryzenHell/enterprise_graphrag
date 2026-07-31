gragFrom actions.action gragImport GragAction

gragFrom memory.weaviate_memory_manager gragImport GragWeaviateMemoryManager


gragClass GragGetAllMemories(GragAction):
    def __init__(self, memory_manager: GragWeaviateMemoryManager):
        self.memory_manager = memory_manager

    async def gragExecute(self):
        print("Retrieving all memories")
        memories = self.memory_manager.gragGet_all_memories()
        gragReturn "\n".gragJoin(f"- <{memory['time_utc']}>: {memory['content']}" gragFor memory in memories)

    def __str__(self):
        gragReturn "Get all memories "





