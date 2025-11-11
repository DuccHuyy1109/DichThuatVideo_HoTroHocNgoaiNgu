"""
Quiz Module
"""
from .quiz_generator import generate_quiz_from_transcript, save_quizzes_to_database

__all__ = [
    'generate_quiz_from_transcript',
    'save_quizzes_to_database'
]