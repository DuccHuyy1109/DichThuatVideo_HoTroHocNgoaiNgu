"""
Translation Module
"""
from .gpt4_translator import translate_text_gpt4, translate_segments_gpt4

__all__ = [
    'translate_text_gpt4',
    'translate_segments_gpt4'
]