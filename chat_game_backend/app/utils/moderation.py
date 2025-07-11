# app/utils/moderation.py

import openai

# Simple abuse keyword list
ABUSE_KEYWORDS = {
    "scam", "idiot", "stupid", "kill", "nonsense", "fool", "dumb", "fraud", "money transfer"
}

def contains_abusive_keyword(text: str) -> bool:
    return any(word in text.lower() for word in ABUSE_KEYWORDS)

def flagged_by_openai(text: str) -> bool:
    try:
        result = openai.Moderation.create(input=text)
        return result["results"][0]["flagged"]
    except Exception:
        return False  # Failsafe if API breaks
