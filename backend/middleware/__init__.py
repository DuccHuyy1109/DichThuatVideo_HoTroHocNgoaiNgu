"""
Middleware package initialization
"""
from .error_handler import register_error_handlers
from .auth_middleware import token_required, get_current_user

__all__ = [
    'register_error_handlers',
    'token_required',
    'get_current_user'
]