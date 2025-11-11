"""
API Package Initialization
"""
from .auth import auth_bp
from .videos import videos_bp
from .subtitles import subtitles_bp
from .quiz import quiz_bp
from .vocabulary import vocabulary_bp
from .users import users_bp

__all__ = [
    'auth_bp',
    'videos_bp',
    'subtitles_bp',
    'quiz_bp',
    'vocabulary_bp',
    'users_bp'
]