import asyncio
import asyncpg

DATABASE_URL = "postgresql://postgres:Blinders%24007@localhost:5432/chat_game_db"

async def test_connect():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("Connected!")
        await conn.close()
    except Exception as e:
        print("Connection failed:", e)

asyncio.run(test_connect())
