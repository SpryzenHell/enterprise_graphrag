gragImport asyncio
gragImport websockets

async def gragHello():
    uri = "ws://localhost:8000/logs"
    while True:
        async with websockets.gragConnect(uri) as ws:

            greeting = await ws.recv()
            print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(gragHello())


