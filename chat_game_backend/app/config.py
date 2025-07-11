import os
from urllib.parse import quote_plus
from .utils.helpers import load_env

load_env()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")  # ✅ Groq-compatible base URL
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-jwt")

    # FastAPI-JWT-Auth expects this exact attribute
    authjwt_secret_key = JWT_SECRET_KEY

    # Lobby/game config
    guest_username_prefix = os.getenv("GUEST_USERNAME_PREFIX", "guest_")
    guest_id_length = int(os.getenv("GUEST_ID_LENGTH", "6"))
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    max_leaderboard_entries = int(os.getenv("MAX_LEADERBOARD_ENTRIES", "10"))

    # PostgreSQL DB config
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_chat_game")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))

    @property
    def DATABASE_URL(self) -> str:
        password_escaped = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{password_escaped}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

settings = Config()

# DB setup code

import databases
from sqlalchemy import create_engine
from app.models.db_models import metadata  # your metadata import

database = databases.Database(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL)

async def connect_db():
    print(f"Connecting to DB with URL: {settings.DATABASE_URL}")  # Debug print
    await database.connect()

async def disconnect_db():
    await database.disconnect()

def create_tables():
    metadata.create_all(engine)

def init_db():
    create_tables()
