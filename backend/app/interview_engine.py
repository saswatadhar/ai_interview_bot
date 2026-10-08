import json
import random
from pathlib import Path


QUESTION_FILE = Path(__file__).resolve().parent / "questions.json"


def load_questions():
    with open(QUESTION_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def detect_topic(answer_text: str):
    questions = load_questions()
    answer_lower = answer_text.lower()

    for topic, data in questions.items():
        for keyword in data.get("keywords", []):
            if keyword.lower() in answer_lower:
                return topic

    return None


def build_question_order(topic: str, max_questions: int = 3):
    questions = load_questions()
    topic_data = questions.get(topic)

    if not topic_data:
        return []

    topic_questions = topic_data.get("questions", [])
    indexes = list(range(len(topic_questions)))

    random.shuffle(indexes)

    return indexes[:max_questions]


def get_question_by_order(topic: str, question_order: list[int], position: int):
    questions = load_questions()
    topic_data = questions.get(topic)

    if not topic_data:
        return None

    topic_questions = topic_data.get("questions", [])

    if position >= len(question_order):
        return None

    question_index = question_order[position]

    if question_index >= len(topic_questions):
        return None

    return topic_questions[question_index]