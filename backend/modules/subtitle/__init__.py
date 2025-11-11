"""
Subtitle Module
"""
from .subtitle_generator import generate_subtitle_file, create_bilingual_subtitle
from .timestamp_sync import sync_timestamps, adjust_timestamps

__all__ = [
    'generate_subtitle_file',
    'create_bilingual_subtitle',
    'sync_timestamps',
    'adjust_timestamps'
]