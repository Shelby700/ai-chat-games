\# 🤖 AI Cha Game Backend



This project powers a \*\*real-time multiplayer AI chat game\*\* where human users and AI bots chat, answer trivia questions, and compete on leaderboards. It features JWT authentication, WebSocket-based communication, moderation tools, and admin control.



---
# Project Structure

ai\_chat\_game\_backend/

├── app/

│   ├── \_\_init\_\_.py

│   ├── config.py

│   ├── main.py

│   ├── models/

│   │   ├── \_\_init\_\_.py

│   │   └── schemas.py

│   ├── services/

│   │   ├── \_\_init\_\_.py

│   │   ├── chatgpt.py

│   │   ├── lobby\_manager.py

│   │   └── game\_loop.py

│   ├── sockets/

│   │   ├── \_\_init\_\_.py

│   │   └── websocket\_handler.py

│   └── utils/

│       ├── \_\_init\_\_.py

│       └── helpers.py

├── requirements.txt

├── README.md

└── .env



⚙️ Architecture Overview



Client (Browser)

&nbsp;    ⬇⬆  WebSocket (FastAPI)

WebSocket Server (FastAPI)

&nbsp;    ⬇⬆  Async API call (OpenAI GPT API)

Language Model (LLM - GPT)



&nbsp;   Users interact with a web-based client via WebSocket.



&nbsp;   The FastAPI WebSocket server routes chat messages, manages lobbies, handles moderation, and optionally invokes GPT responses.



&nbsp;   Trivia/game logic is embedded server-side.



&nbsp;   When needed, messages are forwarded to the LLM API (OpenAI GPT-4) for AI responses.



🧰 Tech Stack

Layer	Stack / Libraries

Backend	Python 3.10+, FastAPI, asyncio, websockets

WebSocket	FastAPI.WebSocket, custom lobby manager

LLM API	OpenAI GPT-3.5 / GPT-4 via openai SDK

Moderation	Custom filter + OpenAI moderation API (optional)

Persistence	Redis (for lobby state \& user scores)

Frontend	HTML/CSS/JS or React (external, not included)

🎯 Prompt Strategy



Bots like GPT-Muse use system prompts to stay on-topic (e.g., trivia or storytelling).



Prompt strategy:



&nbsp;   Light system message like:



&nbsp;       "You are GPT-Muse, a playful bot that helps users play trivia or co-create fun stories."



&nbsp;   User messages are passed directly.



&nbsp;   Bot responses are monitored for trigger phrases like:



&nbsp;       "Would you like to play a game?"

&nbsp;       This initiates bot-to-user game offers.



🚦 Rate Limit \& Abuse Handling

✅ Rate-limiting:



Handled via:



&nbsp;   Cooldowns between AI replies (asyncio.sleep)



&nbsp;   Optional user typing delay throttling (not yet enforced)



🚫 Abuse Handling:



&nbsp;   contains\_abusive\_keyword(text) — static profanity filter



&nbsp;   flagged\_by\_openai(text) — moderation via OpenAI API



&nbsp;   On 3 strikes → user is auto-banned from lobby



🚀 Build \& Run Instructions

1\. ✅ Clone \& Setup



git clone https://github.com/your-repo/chatgame-app.git

cd chatgame-app

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt



2\. ⚙️ Environment



Create .env file:



OPENAI\_API\_KEY=sk-...

REDIS\_URL=redis://localhost:6379



Make sure Redis is running:



redis-server



3\. ▶️ Start Server



uvicorn app.main:app --reload



WebSocket server will be available at:



ws://localhost:8000/ws/{lobby\_id}/{username}?token=...



🧪 Example Commands (in chat)



&nbsp;   "trivia" – starts 10-question quiz



&nbsp;   "/score" – shows personal score



&nbsp;   "/leaderboard" – global top 10



⚠️ Known Limitations



❌ Lobbies are ephemeral unless Redis is persisted



🌱 Future Improvements



Game state persistence in DB (PostgreSQL)



Add voice input/output support



Custom GPT prompts per lobby



Admin dashboard (web interface)



ML-based offensive language detection



Multiplayer trivia modes \& minigames





