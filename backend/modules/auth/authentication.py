"""
Authentication Module
Xử lý đăng ký và đăng nhập
"""
import logging
from datetime import datetime
from database.models import User
from database.db_config import db
from .password_handler import hash_password, check_password
from utils.validators import validate_email, validate_password, validate_username

logger = logging.getLogger(__name__)


def register_user(username, email, password, full_name=None):
    """
    Đăng ký người dùng mới
    
    Args:
        username: Tên đăng nhập
        email: Email
        password: Mật khẩu
        full_name: Họ tên đầy đủ
    
    Returns:
        tuple: (success: bool, user: User or None, message: str)
    """
    try:
        # Validate username
        is_valid, message = validate_username(username)
        if not is_valid:
            return False, None, message
        
        # Validate email
        is_valid, message = validate_email(email)
        if not is_valid:
            return False, None, message
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return False, None, message
        
        # Kiểm tra username đã tồn tại
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return False, None, "Tên đăng nhập đã tồn tại"
        
        # Kiểm tra email đã tồn tại
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return False, None, "Email đã được sử dụng"
        
        # Mã hóa mật khẩu
        password_hash = hash_password(password)
        
        # Tạo user mới
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        # Lưu vào database
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"Đăng ký thành công: {username}")
        
        return True, new_user, "Đăng ký thành công"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi khi đăng ký: {str(e)}")
        return False, None, f"Lỗi khi đăng ký: {str(e)}"


def login_user(username, password):
    """
    Đăng nhập
    
    Args:
        username: Tên đăng nhập hoặc email
        password: Mật khẩu
    
    Returns:
        tuple: (success: bool, user: User or None, message: str)
    """
    try:
        # Tìm user theo username hoặc email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return False, None, "Tên đăng nhập hoặc mật khẩu không đúng"
        
        # Kiểm tra user có active không
        if not user.is_active:
            return False, None, "Tài khoản đã bị vô hiệu hóa"
        
        # Kiểm tra mật khẩu
        if not check_password(password, user.password_hash):
            return False, None, "Tên đăng nhập hoặc mật khẩu không đúng"
        
        # Cập nhật last_login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Đăng nhập thành công: {user.username}")
        
        return True, user, "Đăng nhập thành công"
        
    except Exception as e:
        db.session.rollback()  # Thêm rollback khi có lỗi
        logger.error(f"Lỗi khi đăng nhập: {str(e)}")
        return False, None, f"Lỗi khi đăng nhập: {str(e)}"


def verify_password(user, password):
    """
    Xác thực mật khẩu của user
    
    Args:
        user: User object
        password: Mật khẩu cần kiểm tra
    
    Returns:
        bool: True nếu mật khẩu đúng
    """
    try:
        return check_password(password, user.password_hash)
    except Exception as e:
        logger.error(f"Lỗi khi xác thực mật khẩu: {str(e)}")
        return False


def change_password(user, old_password, new_password):
    """
    Đổi mật khẩu
    
    Args:
        user: User object
        old_password: Mật khẩu cũ
        new_password: Mật khẩu mới
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Kiểm tra mật khẩu cũ
        if not check_password(old_password, user.password_hash):
            return False, "Mật khẩu cũ không đúng"
        
        # Validate mật khẩu mới
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return False, message
        
        # Mã hóa mật khẩu mới
        new_password_hash = hash_password(new_password)
        
        # Cập nhật
        user.password_hash = new_password_hash
        db.session.commit()
        
        logger.info(f"Đổi mật khẩu thành công: {user.username}")
        
        return True, "Đổi mật khẩu thành công"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi khi đổi mật khẩu: {str(e)}")
        return False, f"Lỗi khi đổi mật khẩu: {str(e)}"