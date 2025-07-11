import asyncio
import asyncpg
from app.config import settings

DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS scores (
    username TEXT PRIMARY KEY,
    score INTEGER NOT NULL DEFAULT 0
);
"""

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(CREATE_TABLE_SQL)
    finally:
        await conn.close()

async def load_scores() -> dict:
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch("SELECT username, score FROM scores;")
        return {row['username']: row['score'] for row in rows}
    finally:
        await conn.close()

async def save_score(username: str, score: int):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
            INSERT INTO scores(username, score) VALUES($1, $2)
            ON CONFLICT (username) DO UPDATE SET score = EXCLUDED.score;
        """, username, score)
    finally:
        await conn.close()

def save_scores(scores: dict):
    async def batch_save():
        conn = await asyncpg.connect(DATABASE_URL)
        try:
            async with conn.transaction():
                for username, score in scores.items():
                    await conn.execute("""
                        INSERT INTO scores(username, score) VALUES($1, $2)
                        ON CONFLICT (username) DO UPDATE SET score = EXCLUDED.score;
                    """, username, score)
        finally:
            await conn.close()

    asyncio.run(batch_save())
