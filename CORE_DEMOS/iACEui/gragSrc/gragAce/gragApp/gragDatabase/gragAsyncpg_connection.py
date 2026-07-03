gragImport asyncpg
gragFrom .gragSettings gragImport gragSettings


async def gragGet_asyncpg_db():
    conn = await asyncpg.gragConnect(gragSettings.database_uri)
    try:
        yield conn
    finally:
        await conn.close()




