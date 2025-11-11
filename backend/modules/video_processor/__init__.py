"""
Video Processor Module
"""
from .video_handler import get_video_info, validate_video
from .audio_extractor import extract_audio_from_video

__all__ = [
    'get_video_info',
    'validate_video',
    'extract_audio_from_video'
]