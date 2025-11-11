"""
Authentication Middleware
Xử lý xác thực JWT token
"""
import logging
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from database.models import User
from utils.response_handler import error_response

logger = logging.getLogger(__name__)


def token_required(f):
    """
    Decorator để yêu cầu JWT token hợp lệ
    
    Args:
        f: Function cần được bảo vệ
    
    Returns:
        Wrapped function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Xác thực JWT token
            verify_jwt_in_request()
            
            # Lấy user_id từ token (là string)
            current_user_id_str = get_jwt_identity()
            
            logger.info(f"🔍 Token identity (string): {current_user_id_str}")
            
            # Convert về integer
            try:
                current_user_id = int(current_user_id_str)
                logger.info(f"✅ Converted to int: {current_user_id}")
            except (ValueError, TypeError) as e:
                logger.error(f"❌ Cannot convert to int: {current_user_id_str}")
                return jsonify(error_response(
                    message='Token không hợp lệ',
                    status_code=401
                )), 401
            
            # Kiểm tra user có tồn tại không
            user = User.query.get(current_user_id)
            if not user:
                logger.warning(f"❌ User not found: {current_user_id}")
                return jsonify(error_response(
                    message='Người dùng không tồn tại',
                    status_code=401
                )), 401
            
            # Kiểm tra user có active không
            if not user.is_active:
                logger.warning(f"❌ User inactive: {user.username}")
                return jsonify(error_response(
                    message='Tài khoản đã bị vô hiệu hóa',
                    status_code=401
                )), 401
            
            logger.info(f"✅ Token valid for user: {user.username}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Token verification failed: {str(e)}")
            return jsonify(error_response(
                message='Token không hợp lệ',
                status_code=401,
                error=str(e)
            )), 401
    
    return decorated_function


def get_current_user():
    """
    Lấy thông tin user hiện tại từ JWT token
    
    Returns:
        User object hoặc None
    """
    try:
        # Xác thực JWT token
        verify_jwt_in_request()
        
        # Lấy user_id từ token (là string)
        current_user_id_str = get_jwt_identity()
        
        logger.info(f"🔍 Getting user from token: {current_user_id_str}")
        
        # Convert về integer
        try:
            current_user_id = int(current_user_id_str)
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Cannot convert to int: {current_user_id_str}")
            return None
        
        # Lấy user từ database
        user = User.query.get(current_user_id)
        
        if user:
            logger.info(f"✅ User found: {user.username}")
        else:
            logger.warning(f"❌ User not found: {current_user_id}")
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Get current user error: {str(e)}")
        return None


def optional_token(f):
    """
    Decorator cho phép request với hoặc không có token
    
    Args:
        f: Function cần được bảo vệ
    
    Returns:
        Wrapped function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            pass
        
        return f(*args, **kwargs)
    
    return decorated_function