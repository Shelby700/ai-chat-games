from pydantic import BaseModel, Field
from typing import List, Optional


class LobbyCreate(BaseModel):
    name: str = Field(..., min_length=1)
    is_private: bool = Field(False)
    max_participants: int = Field(..., ge=1)
    ai_bots: int = Field(0, ge=0)


class LobbyInfo(BaseModel):
    id: str
    name: str
    is_private: bool
    max_participants: int
    ai_bots: int
    participants: List[str] = Field(default_factory=list)


class ChatMessage(BaseModel):
    sender: Optional[str]
    text: str = Field(..., min_length=1)
    timestamp: Optional[float]


class JoinLobbySchema(BaseModel):
    username: str
    lobby_id: str


class LeaveLobbySchema(BaseModel):
    username: str
    lobby_id: str


class SendMessageSchema(BaseModel):
    username: str
    lobby_id: str
    text: str
