import os
import time
import uuid
import json
import asyncio
from typing import Dict, List, Optional

import redis
from fastapi import WebSocket
from dotenv import load_dotenv

from app.models.schemas import ChatMessage
from app.services.chatgpt import ask_chatgpt
from app.services.game_loop import next_trivia
from app.utils.moderation import contains_abusive_keyword, flagged_by_openai
from app.services.score_storage import load_scores, save_scores

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


class Lobby:
    def __init__(self, name, is_private, max_participants, ai_bots):
        self.id = str(uuid.uuid4())
        self.name = name
        self.is_private = is_private
        self.max_participants = max_participants
        self.participants: Dict[str, WebSocket] = {}
        self.messages: List[ChatMessage] = []
        self.bot_names = [f"GPT-Muse-{i+1}" for i in range(ai_bots)]
        self.scores: Dict[str, int] = {}
        self.strikes: Dict[str, int] = {}
        self.bot_waiting_state: Dict[str, str] = {}

        self.trivia_mode: Dict[str, bool] = {}
        self.trivia_score: Dict[str, int] = {}
        self.trivia_progress: Dict[str, int] = {}
        self.trivia_current_question: Dict[str, tuple[str, str]] = {}

    def is_full(self):
        return len(self.participants) >= self.max_participants

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "is_private": self.is_private,
            "max_participants": self.max_participants,
            "ai_bots": len(self.bot_names),
            "scores": self.scores,
            "strikes": self.strikes,
        }

    @classmethod
    def from_dict(cls, data):
        lobby = cls(
            name=data["name"],
            is_private=data["is_private"],
            max_participants=data["max_participants"],
            ai_bots=data["ai_bots"],
        )
        lobby.id = data["id"]
        lobby.scores = data.get("scores", {})
        lobby.strikes = data.get("strikes", {})
        return lobby


class LobbyManager:
    def __init__(self):
        self.active_lobbies: Dict[str, Lobby] = {}
        self.banned_users: set[str] = set()
        self.global_scores: Dict[str, int] = load_scores()
        self.trivia_timers: Dict[str, asyncio.Task] = {}
        self.load_lobbies_from_redis()

    def create_lobby(self, name, is_private, max_participants, ai_bots):
        lobby = Lobby(name, is_private, max_participants, ai_bots)
        self.active_lobbies[lobby.id] = lobby
        self._save_lobby_to_redis(lobby)
        return lobby

    def join_lobby(self, lobby_id, username):
        if username in self.banned_users:
            raise ValueError("User is banned.")
        lobby = self.active_lobbies.get(lobby_id)
        if not lobby:
            raise ValueError("Lobby not found.")
        if lobby.is_full():
            raise ValueError("Lobby is full.")
        if username in lobby.participants:
            raise ValueError("User already joined.")
        lobby.scores.setdefault(username, 0)
        lobby.strikes.setdefault(username, 0)

    async def connect(self, lobby_id, username, websocket: WebSocket):
        lobby = self.active_lobbies.get(lobby_id)
        if not lobby or username in self.banned_users:
            await websocket.send_text("❌ Connection not allowed.")
            await websocket.close()
            return
        if lobby.is_full():
            await websocket.send_text("❌ Lobby is full.")
            await websocket.close()
            return
        lobby.participants[username] = websocket
        lobby.scores.setdefault(username, 0)
        lobby.strikes.setdefault(username, 0)
        lobby.trivia_mode[username] = False
        lobby.trivia_score[username] = 0
        lobby.trivia_progress[username] = 0
        await self.broadcast(lobby_id, f"✅ {username} joined the lobby.")
        if lobby.bot_names:
            await self.broadcast(lobby_id, f"🤖 Active bots: {', '.join(lobby.bot_names)}")

    async def disconnect(self, lobby_id, username):
        lobby = self.active_lobbies.get(lobby_id)
        if lobby and username in lobby.participants:
            del lobby.participants[username]
            await self.broadcast(lobby_id, f"👋 {username} left the lobby.")

    async def send_message(self, lobby_id, username, text):
        lobby = self.active_lobbies.get(lobby_id)
        if not lobby:
            return

        cmd = text.lower().strip()

        # Abuse filtering
        if contains_abusive_keyword(cmd) or flagged_by_openai(cmd):
            lobby.strikes[username] += 1
            if lobby.strikes[username] >= 3:
                self.banned_users.add(username)
                await self.broadcast(lobby_id, f"🚫 {username} was banned.")
                await self.disconnect(lobby_id, username)
                return
            await self.broadcast(lobby_id, f"⚠️ {username}, warning {lobby.strikes[username]}/3")
            return

        # Start Trivia Mode
        if cmd == "trivia":
            lobby.trivia_mode[username] = True
            lobby.trivia_score[username] = 0
            lobby.trivia_progress[username] = 0
            await self._ask_next_trivia(lobby_id, username)
            return

        # Ongoing trivia answers
        if lobby.trivia_mode.get(username):
            question, answer = lobby.trivia_current_question.get(username, ("", ""))
            if cmd == answer.lower():
                lobby.trivia_score[username] += 1
                await self.broadcast(lobby_id, f"✅ {username}, correct!")
            else:
                await self.broadcast(lobby_id, f"❌ {username}, wrong. Correct answer was: {answer}")
            await self._ask_next_trivia(lobby_id, username)
            return

        # Normal commands
        if cmd == "/score":
            await self.broadcast(lobby_id, f"📊 {username}'s score: {lobby.scores[username]}")
            return
        if cmd == "/leaderboard":
            top = sorted(self.global_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            await self.broadcast(lobby_id, "🏆 Leaderboard:\n" + "\n".join(f"{u}: {s}" for u, s in top))
            return

        # Normal message
        lobby.messages.append(ChatMessage(sender=username, text=text, timestamp=time.time()))
        await self.broadcast(lobby_id, f"{username}: {text}")

        # AI response
        for bot in lobby.bot_names:
            asyncio.create_task(self._ai_reply(lobby_id, bot, text))

    async def _ask_next_trivia(self, lobby_id: str, username: str):
        lobby = self.active_lobbies.get(lobby_id)
        if not lobby:
            return
        progress = lobby.trivia_progress.get(username, 0)
        if progress >= 10:
            score = lobby.trivia_score.get(username, 0)
            await self.broadcast(lobby_id, f"🎯 {username} completed Trivia! Final score: {score}/10")
            lobby.trivia_mode[username] = False
            return
        q, a = next_trivia()
        lobby.trivia_current_question[username] = (q, a)
        lobby.trivia_progress[username] = progress + 1
        await self.broadcast(lobby_id, f"🧠 Trivia Q{progress + 1} for {username}: {q}")

    async def _ai_reply(self, lobby_id, bot_name, user_text):
        await asyncio.sleep(2)
        reply = await ask_chatgpt(user_text)
        lobby = self.active_lobbies.get(lobby_id)
        if not lobby:
            return
        if "play a game" in reply.lower() or "would you like" in reply.lower():
            lobby.bot_waiting_state[bot_name] = reply
            return
        lobby.messages.append(ChatMessage(sender=bot_name, text=reply, timestamp=time.time()))
        await self.broadcast(lobby_id, f"{bot_name}: {reply}")

    async def broadcast(self, lobby_id, text):
        lobby = self.active_lobbies.get(lobby_id)
        if lobby:
            for ws in list(lobby.participants.values()):
                try:
                    await ws.send_text(text)
                except:
                    pass

    async def broadcast_scores(self, lobby_id):
        lobby = self.active_lobbies.get(lobby_id)
        if lobby:
            scores = "\n".join([f"{u}: {s}" for u, s in lobby.scores.items()])
            await self.broadcast(lobby_id, f"🏆 Current Scores:\n{scores}")

    def list_lobbies(self):
        return [
            {
                "id": lobby.id,
                "name": lobby.name,
                "is_private": lobby.is_private,
                "participant_count": len(lobby.participants),
                "max_participants": lobby.max_participants,
                "ai_bots": len(lobby.bot_names),
            }
            for lobby in self.active_lobbies.values()
        ]

    def _save_lobby_to_redis(self, lobby: Lobby):
        redis_client.hset("lobbies", lobby.id, json.dumps(lobby.to_dict()))

    def load_lobbies_from_redis(self):
        all_lobbies = redis_client.hgetall("lobbies")
        for lobby_id, lobby_data in all_lobbies.items():
            try:
                data = json.loads(lobby_data)
                lobby = Lobby.from_dict(data)
                self.active_lobbies[lobby.id] = lobby
            except Exception as e:
                print(f"Failed to load lobby {lobby_id}: {e}")
