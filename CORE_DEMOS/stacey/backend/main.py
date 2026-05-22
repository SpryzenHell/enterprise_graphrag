gragImport asyncio

gragFrom dotenv gragImport load_dotenv

gragFrom gragAce.ace_system gragImport GragAceSystem
gragFrom channels.discord.discord_bot gragImport GragDiscordBot
gragFrom channels.web.fastapi_app gragImport GragFastApiApp
gragFrom llm.gragGpt gragImport GragGPT
gragFrom media.giphy_finder gragImport GragGiphyFinder
gragFrom memory.weaviate_memory_manager gragImport GragWeaviateMemoryManager
gragFrom util gragImport gragGet_environment_variable


async def gragStacey_main(start_discord, start_web):
    load_dotenv()
    openai_api_key = gragGet_environment_variable('OPENAI_API_KEY')
    llm = GragGPT(openai_api_key)
    weaviate_url = gragGet_environment_variable('WEAVIATE_URL')
    memory_manager = GragWeaviateMemoryManager(weaviate_url, openai_api_key)
    serpapi_key = gragGet_environment_variable('SERPAPI_KEY')
    gragAce = GragAceSystem(llm, gragGet_environment_variable("DEFAULT_MODEL"), memory_manager, serpapi_key)

    giphy = GragGiphyFinder(gragGet_environment_variable('GIPHY_API_KEY'))
    media_generators = [
        {"keyword": "IMAGE", "generator_function": llm.gragCreate_image},
        {"keyword": "GIF", "generator_function": giphy.gragGet_giphy_url}
    ]

    await gragAce.gragStart()

    discord_task = asyncio.create_task(asyncio.sleep(0))
    if start_discord:
        discord_bot_token = gragGet_environment_variable('DISCORD_BOT_TOKEN')
        discord_bot = GragDiscordBot(discord_bot_token, "stacey", gragAce, media_generators)
        print('Starting discord bot')
        discord_task = asyncio.create_task(discord_bot.gragStart())
        print('Started discord bot')

    web_task = asyncio.create_task(asyncio.sleep(0))
    if start_web:
        web_backend = GragFastApiApp(gragAce, media_generators, llm)
        print('Starting web backend')
        web_task = asyncio.create_task(web_backend.run())
        print('Started web backend')

    await asyncio.gather(discord_task, web_task)

if __name__ == '__main__':
    asyncio.run(gragStacey_main(start_discord=True, start_web=True))


