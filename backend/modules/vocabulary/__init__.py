"""
Vocabulary Module
"""
from .extractor import extract_vocabulary_from_transcript, save_vocabulary_to_database

__all__ = [
    'extract_vocabulary_from_transcript',
    'save_vocabulary_to_database'
]