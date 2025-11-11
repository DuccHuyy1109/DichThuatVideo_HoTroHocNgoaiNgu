"""
File Handler Utilities
Xử lý các thao tác với file
"""
import os
import logging
import uuid
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


def save_uploaded_file(file, upload_folder, subfolder=''):
    """
    Lưu file được upload
    
    Args:
        file: File object từ request
        upload_folder: Thư mục lưu file
        subfolder: Thư mục con (optional)
    
    Returns:
        tuple: (success: bool, file_path: str, message: str)
    """
    try:
        if not file:
            return False, None, "Không có file được upload"
        
        # Tạo tên file an toàn
        original_filename = secure_filename(file.filename)
        
        # Tạo tên file unique
        unique_filename = generate_filename(original_filename)
        
        # Tạo đường dẫn đầy đủ
        save_path = os.path.join(upload_folder, subfolder)
        os.makedirs(save_path, exist_ok=True)
        
        # Đường dẫn file hoàn chỉnh
        file_path = os.path.join(save_path, unique_filename)
        
        # Lưu file
        file.save(file_path)
        
        logger.info(f"File đã được lưu: {file_path}")
        
        return True, file_path, "Lưu file thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi lưu file: {str(e)}")
        return False, None, f"Lỗi khi lưu file: {str(e)}"


def delete_file(file_path):
    """
    Xóa file
    
    Args:
        file_path: Đường dẫn file cần xóa
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not file_path or not os.path.exists(file_path):
            return False, "File không tồn tại"
        
        os.remove(file_path)
        logger.info(f"File đã được xóa: {file_path}")
        
        return True, "Xóa file thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi xóa file: {str(e)}")
        return False, f"Lỗi khi xóa file: {str(e)}"


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


def get_file_size(file_path):
    """
    Lấy kích thước file
    
    Args:
        file_path: Đường dẫn file
    
    Returns:
        int: Kích thước file (bytes)
    """
    try:
        if not os.path.exists(file_path):
            return 0
        
        return os.path.getsize(file_path)
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy kích thước file: {str(e)}")
        return 0


def create_directory(directory_path):
    """
    Tạo thư mục
    
    Args:
        directory_path: Đường dẫn thư mục
    
    Returns:
        bool: True nếu thành công
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Lỗi khi tạo thư mục: {str(e)}")
        return False


def file_exists(file_path):
    """
    Kiểm tra file có tồn tại không
    
    Args:
        file_path: Đường dẫn file
    
    Returns:
        bool: True nếu file tồn tại
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)


def generate_filename(original_filename):
    """
    Tạo tên file unique
    
    Args:
        original_filename: Tên file gốc
    
    Returns:
        str: Tên file unique
    """
    # Lấy extension
    ext = get_file_extension(original_filename)
    
    # Tạo UUID
    unique_id = str(uuid.uuid4())
    
    # Tạo tên file mới
    if ext:
        return f"{unique_id}.{ext}"
    else:
        return unique_id


def sanitize_filename(filename):
    """
    Làm sạch tên file
    
    Args:
        filename: Tên file
    
    Returns:
        str: Tên file đã được làm sạch
    """
    # Sử dụng secure_filename của Werkzeug
    return secure_filename(filename)