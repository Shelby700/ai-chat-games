from openai import OpenAI
from app.config import settings

# ✅ Support Groq or any OpenAI-compatible provider via base_url
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_API_BASE
)

def ask_chatgpt(prompt: str) -> str:
    """
    Sends a prompt to OpenAI-compatible API and returns the assistant's response.
    """
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant in a chat game."},
                {"role": "user", "content": prompt}
            ],
            temperature=settings.OPENAI_TEMPERATURE
        )
        return response.choices[0].message.content
    except Exception as e:
        # Optional: Add logging or return fallback message
        return f"⚠️ Error from AI: {str(e)}"

print(f"🚨 OpenAI model in use: {settings.OPENAI_MODEL} (via {settings.OPENAI_API_BASE})")
