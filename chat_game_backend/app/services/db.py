import databases
from sqlalchemy import create_engine, MetaData
from app.config import settings

database = databases.Database(settings.DATABASE_URL)  # async DB connection
engine = create_engine(settings.DATABASE_URL)         # sync engine for metadata

metadata = MetaData()  # You can import your models’ metadata here and add it

async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()

def create_tables():
    metadata.create_all(engine)

async def init_db():
    # Connect DB and create tables (sync call wrapped in thread by default)
    await connect_db()
    create_tables()
