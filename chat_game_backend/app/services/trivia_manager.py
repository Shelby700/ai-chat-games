# app/services/trivia_manager.py

import random
from typing import Dict, Optional

TRIVIA_QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "answers": ["paris"]
    },
    {
        "question": "Who wrote 'Hamlet'?",
        "answers": ["shakespeare", "william shakespeare"]
    },
    {
        "question": "What planet is known as the Red Planet?",
        "answers": ["mars"]
    },
    {
        "question": "How many legs does a spider have?",
        "answers": ["8", "eight"]
    },
]

class TriviaGameManager:
    def __init__(self):
        self.current_question: Optional[str] = None
        self.correct_answers: list[str] = []
        self.scores: Dict[str, int] = {}

    def start_new_round(self):
        q = random.choice(TRIVIA_QUESTIONS)
        self.current_question = q["question"]
        self.correct_answers = q["answers"]

    def check_answer(self, username: str, answer: str) -> bool:
        if not self.current_question:
            return False
        if answer.strip().lower() in self.correct_answers:
            self.scores[username] = self.scores.get(username, 0) + 1
            return True
        return False

    def get_scoreboard(self):
        return dict(sorted(self.scores.items(), key=lambda x: x[1], reverse=True))

    def reset(self):
        self.current_question = None
        self.correct_answers = []
        self.scores = {}
