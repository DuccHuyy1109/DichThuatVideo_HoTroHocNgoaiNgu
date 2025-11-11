"""
Authentication Module
"""
from .authentication import register_user, login_user, verify_password, change_password
from .password_handler import hash_password, check_password

__all__ = [
    'register_user',
    'login_user',
    'verify_password',
    'change_password',
    'hash_password',
    'check_password'
]