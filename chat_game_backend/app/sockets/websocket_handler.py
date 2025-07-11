import logging
import json
import traceback
from fastapi import WebSocket
from jwt import decode as jwt_decode, InvalidTokenError, ExpiredSignatureError

from app.services.lobby_manager import LobbyManager
from app.config import settings
from app.services.chatgpt import ask_chatgpt  # ← import this

logger = logging.getLogger(__name__)
JWT_SECRET_KEY = settings.authjwt_secret_key

async def handle_websocket(websocket: WebSocket, lobby_id: str, username: str, token: str, manager: LobbyManager):
    try:
        payload = jwt_decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("sub") != username:
            logger.warning("JWT subject does not match username.")
            await websocket.close(code=4003)
            return
    except (InvalidTokenError, ExpiredSignatureError) as e:
        logger.warning(f"Invalid or expired JWT token: {e}")
        await websocket.close(code=4001)
        return
    except Exception as e:
        logger.error(f"JWT validation failed: {e}")
        await websocket.close(code=4002)
        return

    if lobby_id not in manager.active_lobbies:
        logger.warning(f"Lobby {lobby_id} does not exist.")
        await websocket.close(code=4004)
        return

    await websocket.accept()
    logger.info(f"🟢 WebSocket accepted for {username} in {lobby_id}")

    try:
        await manager.connect(lobby_id, username, websocket)
        await manager.broadcast(lobby_id, f"✅ {username} joined the room")

        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received message from {username}: {data}")
            try:
                parsed = json.loads(data)
                action = parsed.get("action")

                if action == "send_message":
                    text = parsed.get("text")
                    if not text:
                        await websocket.send_text(json.dumps({"error": "Missing 'text' field"}))
                        continue

                    await manager.send_message(lobby_id, username, text)

                    # 👇 BOT LOGIC: If GPT bot is in this lobby, reply after user speaks
                    lobby = manager.active_lobbies[lobby_id]
                    bot_name = None
                    for b in lobby.bot_names:
                        if b.startswith("GPT-Muse-"):
                            bot_name = b
                            break

                    if bot_name:
                        logger.info(f"🤖 Triggering AI bot: {bot_name} with prompt: {text}")
                        ai_response = ask_chatgpt(text)
                        await manager.send_message(lobby_id, bot_name, ai_response)

                elif action == "leave":
                    await manager.broadcast(lobby_id, f"🚪 {username} left the room")
                    await manager.disconnect(lobby_id, username)
                    await websocket.close()
                    break

                else:
                    await websocket.send_text(json.dumps({"error": "Unknown action"}))

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {username}")
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))

            except Exception as e:
                logger.warning(f"Message handling error: {e}")
                await websocket.send_text(json.dumps({"error": "Server error processing message"}))

    except Exception as e:
        logger.error(f"WebSocket error for {username}: {e}")
        traceback.print_exc()

    finally:
        await manager.disconnect(lobby_id, username)
        logger.info(f"🔴 {username} disconnected from {lobby_id}")
