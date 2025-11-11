"""
Validators Utilities
Các hàm validate dữ liệu đầu vào
"""
import re
import os
from email_validator import validate_email as email_validate, EmailNotValidError


def validate_email(email):
    """
    Validate email address
    
    Args:
        email: Email cần validate
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not email:
        return False, "Email không được để trống"
    
    try:
        # Validate email format
        valid = email_validate(email)
        return True, "Email hợp lệ"
    except EmailNotValidError as e:
        return False, str(e)


def validate_password(password):
    """
    Validate password strength
    
    Args:
        password: Mật khẩu cần validate
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not password:
        return False, "Mật khẩu không được để trống"
    
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"
    
    if len(password) > 50:
        return False, "Mật khẩu không được vượt quá 50 ký tự"
    
    # Kiểm tra có chữ và số
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not (has_letter and has_digit):
        return False, "Mật khẩu phải chứa cả chữ và số"
    
    return True, "Mật khẩu hợp lệ"


def validate_username(username):
    """
    Validate username
    
    Args:
        username: Username cần validate
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not username:
        return False, "Username không được để trống"
    
    if len(username) < 3:
        return False, "Username phải có ít nhất 3 ký tự"
    
    if len(username) > 50:
        return False, "Username không được vượt quá 50 ký tự"
    
    # Chỉ cho phép chữ, số, dấu gạch dưới và gạch ngang
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username chỉ được chứa chữ, số, dấu _ và -"
    
    return True, "Username hợp lệ"


def validate_video_file(filename, allowed_extensions):
    """
    Validate video file
    
    Args:
        filename: Tên file
        allowed_extensions: Set các extension được phép
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not filename:
        return False, "Tên file không được để trống"
    
    # Lấy extension
    ext = get_file_extension(filename)
    
    if not ext:
        return False, "File không có extension"
    
    if ext not in allowed_extensions:
        return False, f"Định dạng file không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
    
    return True, "File hợp lệ"


def validate_language_code(language_code, supported_languages):
    """
    Validate mã ngôn ngữ
    
    Args:
        language_code: Mã ngôn ngữ (vd: en, vi)
        supported_languages: List các ngôn ngữ được hỗ trợ
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not language_code:
        return False, "Mã ngôn ngữ không được để trống"
    
    if language_code not in supported_languages:
        return False, f"Ngôn ngữ không được hỗ trợ. Các ngôn ngữ hỗ trợ: {', '.join(supported_languages)}"
    
    return True, "Mã ngôn ngữ hợp lệ"


def get_file_extension(filename):
    """
    Lấy extension của file
    
    Args:
        filename: Tên file
    
    Returns:
        str: Extension (lowercase, không có dấu chấm)
    """
    if '.' not in filename:
        return ''
    
    return filename.rsplit('.', 1)[1].lower()


def validate_duration(duration, max_duration):
    """
    Validate thời lượng video
    
    Args:
        duration: Thời lượng (giây)
        max_duration: Thời lượng tối đa cho phép
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if duration <= 0:
        return False, "Thời lượng video không hợp lệ"
    
    if duration > max_duration:
        return False, f"Video quá dài. Thời lượng tối đa: {max_duration/60} phút"
    
    return True, "Thời lượng hợp lệ"