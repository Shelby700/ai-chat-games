# app/services/game_loop.py

import random

TRIVIA_QUESTIONS = [
    {"question": "What is the capital of France?", "answer": "paris"},
    {"question": "What planet is known as the Red Planet?", "answer": "mars"},
    {"question": "Who wrote 'Hamlet'?", "answer": "shakespeare"},
    {"question": "What gas do plants absorb?", "answer": "carbon dioxide"},
    {"question": "How many continents are there?", "answer": "7"},
    {"question": "What is the largest ocean on Earth?", "answer": "pacific"},
    {"question": "Who painted the Mona Lisa?", "answer": "leonardo da vinci"},
    {"question": "What is the hardest natural substance?", "answer": "diamond"},
    {"question": "What is the smallest prime number?", "answer": "2"},
    {"question": "Who was the first man on the moon?", "answer": "neil armstrong"},
    {"question": "Which planet is closest to the sun?", "answer": "mercury"},
    {"question": "What is the capital of Japan?", "answer": "tokyo"},
    {"question": "Which animal is known as the king of the jungle?", "answer": "lion"},
    {"question": "What is the freezing point of water in Celsius?", "answer": "0"},
    {"question": "How many legs does a spider have?", "answer": "8"},
    {"question": "What is the tallest mountain in the world?", "answer": "everest"},
    {"question": "What is the chemical symbol for water?", "answer": "h2o"},
    {"question": "Which country is known for pizza?", "answer": "italy"},
    {"question": "What is the national language of Brazil?", "answer": "portuguese"},
    {"question": "What is the square root of 64?", "answer": "8"},
    {"question": "What do bees produce?", "answer": "honey"},
    {"question": "Which bird can mimic human speech?", "answer": "parrot"},
    {"question": "Which planet has rings?", "answer": "saturn"},
    {"question": "What is the capital of Australia?", "answer": "canberra"},
    {"question": "Which animal is the largest mammal?", "answer": "blue whale"},
    {"question": "Which country has the most people?", "answer": "china"},
    {"question": "How many hours are in a day?", "answer": "24"},
    {"question": "What is the opposite of north?", "answer": "south"},
    {"question": "How many days are in a leap year?", "answer": "366"},
    {"question": "What is the main ingredient in bread?", "answer": "flour"}
]

class TriviaManager:
    def __init__(self):
        self.active_questions = {}  # lobby_id -> current question

    def get_question(self, lobby_id: str) -> str:
        q = random.choice(TRIVIA_QUESTIONS)
        self.active_questions[lobby_id] = q
        return q["question"]

    def check_answer(self, lobby_id: str, answer: str) -> bool:
        correct = self.active_questions.get(lobby_id, {}).get("answer", "").lower()
        return answer.strip().lower() == correct

    def clear(self, lobby_id: str):
        self.active_questions.pop(lobby_id, None)

# Instance used in LobbyManager
trivia = TriviaManager()

# Optional utility
def next_trivia():
    q = random.choice(TRIVIA_QUESTIONS)
    return q["question"], q["answer"]
