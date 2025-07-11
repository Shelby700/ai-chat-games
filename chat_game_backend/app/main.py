import time
import random
import string
import logging
from typing import List
from fastapi import FastAPI, WebSocket, HTTPException, status, Depends, Query, Path
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from jwt import ExpiredSignatureError
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.models.schemas import LobbyCreate, LobbyInfo
from app.models.auth_schemas import RegisterSchema, LoginSchema, TokenResponse, AdminLoginSchema
from app.services.lobby_manager import LobbyManager
from app.models.users import register_user, authenticate_user, get_user_role
from app.utils.auth_config import AuthSettings
from app.services.score_storage import load_scores
from app.sockets.websocket_handler import handle_websocket
from app.services.db import init_db

# ✅ Redis client to restore persisted lobbies
from app.utils.redis_client import redis_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Chat Game Backend")

# SINGLE instance of LobbyManager
manager = LobbyManager()

@AuthJWT.load_config
def get_config():
    return AuthSettings()

@app.exception_handler(AuthJWTException)
def auth_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.exception_handler(ExpiredSignatureError)
def expired_token_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": "Token has expired. Please log in again."})

# Config-driven values from settings
GUEST_USERNAME_PREFIX = settings.guest_username_prefix
GUEST_ID_LENGTH = settings.guest_id_length
ADMIN_USERNAME = settings.admin_username
MAX_TOP_LEADERBOARD = settings.max_leaderboard_entries

@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info(f"App started with admin='{ADMIN_USERNAME}', guest_prefix='{GUEST_USERNAME_PREFIX}', leaderboard_top_n={MAX_TOP_LEADERBOARD}'")

# Authentication Endpoints
@app.post("/auth/register", response_model=dict)
def register(data: RegisterSchema):
    role = "admin" if data.username == ADMIN_USERNAME else "user"
    success = register_user(data.username, data.password, role=role)
    if not success:
        raise HTTPException(status_code=400, detail="Username already taken")
    return {"message": "User registered successfully."}

@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginSchema, Authorize: AuthJWT = Depends()):
    if not authenticate_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    role = get_user_role(data.username)
    access_token = Authorize.create_access_token(subject=data.username, user_claims={"role": role})
    return {"access_token": access_token}

@app.post("/auth/admin/login", response_model=TokenResponse)
def admin_login(data: AdminLoginSchema, Authorize: AuthJWT = Depends()):
    if data.username != ADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Only admin can log in here")
    if not authenticate_user(data.username, data.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    access_token = Authorize.create_access_token(subject=data.username, user_claims={"role": "admin"})
    return {"access_token": access_token}

@app.post("/auth/guest-login", response_model=TokenResponse)
def guest_login(Authorize: AuthJWT = Depends()):
    guest_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=GUEST_ID_LENGTH))
    guest_username = f"{GUEST_USERNAME_PREFIX}{guest_id}"
    access_token = Authorize.create_access_token(subject=guest_username, user_claims={"role": "guest"})
    return {"access_token": access_token}

# Lobby Management
@app.post("/lobbies/", response_model=LobbyInfo, status_code=status.HTTP_201_CREATED)
def create_lobby(data: LobbyCreate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    if data.max_participants < 1:
        raise HTTPException(status_code=400, detail="max_participants must be at least 1")
    lobby = manager.create_lobby(
        name=data.name,
        is_private=data.is_private,
        max_participants=data.max_participants,
        ai_bots=data.ai_bots,
    )
    return LobbyInfo(
        id=lobby.id,
        name=lobby.name,
        is_private=lobby.is_private,
        max_participants=lobby.max_participants,
        ai_bots=len(lobby.bot_names),
        participants=list(lobby.participants.keys()) + lobby.bot_names
    )

@app.get("/lobbies/", response_model=List[dict])
def list_lobbies(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return manager.list_lobbies()

@app.post("/lobbies/{lobby_id}/join", response_model=dict)
def join_lobby(lobby_id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    if lobby_id not in manager.active_lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")
    manager.join_lobby(lobby_id, username)
    return {"message": f"{username} joined lobby {lobby_id}"}

@app.get("/lobbies/{lobby_id}", response_model=LobbyInfo)
def get_lobby(lobby_id: str = Path(..., description="The ID of the lobby to retrieve"), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    lobby = manager.active_lobbies.get(lobby_id)
    if not lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")
    return LobbyInfo(
        id=lobby.id,
        name=lobby.name,
        is_private=lobby.is_private,
        max_participants=lobby.max_participants,
        ai_bots=len(lobby.bot_names),
        participants=list(lobby.participants.keys()) + lobby.bot_names
    )

# WebSocket Endpoint
@app.websocket("/ws/{lobby_id}/{username}")
async def websocket_route(websocket: WebSocket, lobby_id: str, username: str, token: str = Query(...)):
    await handle_websocket(websocket, lobby_id, username, token, manager)

# Moderation & Reporting
class ReportRequest(BaseModel):
    offender: str
    reason: str

abuse_reports: List[dict] = []

@app.get("/moderation/banlist", response_model=List[str])
def get_ban_list(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return list(manager.banned_users)

@app.post("/moderation/ban", response_model=dict)
def ban_user(username: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    manager.banned_users.add(username.strip().lower())
    return {"message": f"🚫 '{username}' has been banned."}

@app.post("/moderation/unban", response_model=dict)
def unban_user(username: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    manager.banned_users.discard(username.strip().lower())
    return {"message": f"✅ '{username}' has been unbanned."}

@app.post("/moderation/report", response_model=dict)
def report_user(data: ReportRequest, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    reporter = Authorize.get_jwt_subject()
    if data.offender.strip().lower() == reporter.strip().lower():
        raise HTTPException(status_code=400, detail="You cannot report yourself.")
    abuse_reports.append({
        "reporter": reporter,
        "offender": data.offender.strip().lower(),
        "reason": data.reason.strip(),
        "timestamp": time.time()
    })
    return {"message": f"✅ Report submitted against '{data.offender}'."}

@app.get("/moderation/reports", response_model=List[dict])
def get_reports(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    role = Authorize.get_raw_jwt().get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only.")
    return abuse_reports

# Leaderboard
@app.get("/leaderboard", response_model=List[dict])
def leaderboard(top_n: int = MAX_TOP_LEADERBOARD, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    scores = load_scores()
    return [{"username": user, "score": score} for user, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]]

# OpenAPI schema with JWT security
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version="0.1.0",
        description="Backend for AI chat-based game with JWT auth",
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
