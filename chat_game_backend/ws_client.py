import asyncio
import websockets
import json

# === Replace with your actual values ===
LOBBY_ID = "0b799d2f-a315-4daf-9c71-4d696e327982"  # ✅ Your latest joined lobby ID
USERNAME = "testuser3"
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0dXNlcjMiLCJpYXQiOjE3NTIxODU3MzksIm5iZiI6MTc1MjE4NTczOSwianRpIjoiNjg4Y2E1OGEtN2JkNC00NjhhLTgzN2QtNjQ2Yzg3M2ZmODQ3IiwiZXhwIjoxNzUyMTg5MzM5LCJ0eXBlIjoiYWNjZXNzIiwiZnJlc2giOmZhbHNlLCJyb2xlIjoidXNlciJ9.Tp4E70XrJsFTnvcOJ9YZez1bihj0iB8CwyeeB3MN--Y"

# === WebSocket URL ===
ws_url = f"ws://127.0.0.1:8000/ws/{LOBBY_ID}/{USERNAME}?token={TOKEN}"

async def test_websocket():
    try:
        print(f"🔌 Connecting to WebSocket: {ws_url}")
        async with websockets.connect(ws_url) as websocket:
            print("✅ Connected to WebSocket")

            # ✅ Send a properly formatted message (JSON)
            message = {
                "action": "send_message",
                "text": "Hello bot, tell me a joke!"
            }
            await websocket.send(json.dumps(message))
            print("📤 Sent message to bot.")

            # 📩 Listen for responses (including bot reply)
            while True:
                msg = await websocket.recv()
                print("📨 Server:", msg)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
    except Exception as e:
        print(f"⚠️ WebSocket error: {e}")

# Run the WebSocket test client
if __name__ == "__main__":
    asyncio.run(test_websocket())
