import os
from dotenv import load_dotenv

def load_env():
    load_dotenv()  # read .env into os.environ
    # ✅ Optional debug log to verify critical env vars are loaded correctly
    print("[DEBUG] Environment loaded.")
    print("[DEBUG] JWT_SECRET_KEY =", os.getenv("JWT_SECRET_KEY"))
    print("[DEBUG] OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY")[:6] + "..." if os.getenv("OPENAI_API_KEY") else "Not Set")

def get_env(var_name: str, default=None):
    return os.getenv(var_name, default)
