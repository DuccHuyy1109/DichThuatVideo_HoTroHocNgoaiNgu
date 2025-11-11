"""
Password Handler
Xử lý mã hóa và kiểm tra mật khẩu
"""
import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password):
    """
    Mã hóa mật khẩu bằng bcrypt
    
    Args:
        password: Mật khẩu cần mã hóa
    
    Returns:
        str: Mật khẩu đã được mã hóa
    """
    try:
        # Chuyển password sang bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt và hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Trả về string
        return hashed.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Lỗi khi mã hóa mật khẩu: {str(e)}")
        raise


def check_password(password, hashed_password):
    """
    Kiểm tra mật khẩu với hash
    
    Args:
        password: Mật khẩu cần kiểm tra
        hashed_password: Hash password đã lưu
    
    Returns:
        bool: True nếu mật khẩu đúng
    """
    try:
        # Chuyển sang bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Kiểm tra
        return bcrypt.checkpw(password_bytes, hashed_bytes)
        
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra mật khẩu: {str(e)}")
        return False