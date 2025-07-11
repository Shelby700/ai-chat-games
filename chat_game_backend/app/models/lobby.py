from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Lobby(Base):
    __tablename__ = "lobbies"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_private = Column(Boolean, default=False)
    max_participants = Column(Integer, default=10)
    # Store bots count or names as JSON or string, here simple count:
    ai_bots = Column(Integer, default=0)

    # Participants: relationship, optional, depends on your design

class LobbyParticipant(Base):
    __tablename__ = "lobby_participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lobby_id = Column(String, ForeignKey("lobbies.id"), nullable=False)
    username = Column(String, nullable=False)
