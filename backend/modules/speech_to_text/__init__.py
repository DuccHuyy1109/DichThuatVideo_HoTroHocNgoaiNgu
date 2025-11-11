"""
Speech to Text Module
"""
from .whisper_handler import transcribe_audio_whisper
from .language_detector import detect_language

__all__ = [
    'transcribe_audio_whisper',
    'detect_language'
]