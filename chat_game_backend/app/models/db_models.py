from sqlalchemy import Table, Column, String, Integer, Boolean, MetaData, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

metadata = MetaData()

lobbies = Table(
    "lobbies",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("name", String, nullable=False),
    Column("is_private", Boolean, default=False),
    Column("max_participants", Integer, nullable=False),
    Column("bot_names", JSON, default=[]),
)
