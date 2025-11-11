"""
Helper Utilities
Các hàm tiện ích chung
"""
import re
import uuid
from datetime import datetime, timedelta


def format_duration(seconds):
    """
    Format thời lượng từ giây sang định dạng HH:MM:SS
    
    Args:
        seconds: Số giây
    
    Returns:
        str: Thời lượng định dạng HH:MM:SS
    """
    if not seconds or seconds < 0:
        return "00:00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_duration_readable(seconds):
    """
    Format thời lượng thành dạng dễ đọc
    
    Args:
        seconds: Số giây
    
    Returns:
        str: Thời lượng dễ đọc (vd: "1 giờ 30 phút")
    """
    if not seconds or seconds < 0:
        return "0 giây"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} giờ")
    if minutes > 0:
        parts.append(f"{minutes} phút")
    if secs > 0 and hours == 0:
        parts.append(f"{secs} giây")
    
    return " ".join(parts) if parts else "0 giây"


def generate_unique_id():
    """
    Tạo ID unique
    
    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())


def generate_filename(original_filename):
    """
    Tạo tên file unique
    
    Args:
        original_filename: Tên file gốc
    
    Returns:
        str: Tên file unique
    """
    from .file_handler import get_file_extension
    
    ext = get_file_extension(original_filename)
    unique_id = generate_unique_id()
    
    if ext:
        return f"{unique_id}.{ext}"
    return unique_id


def sanitize_filename(filename):
    """
    Làm sạch tên file
    
    Args:
        filename: Tên file
    
    Returns:
        str: Tên file đã được làm sạch
    """
    # Loại bỏ các ký tự đặc biệt
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Thay thế khoảng trắng bằng underscore
    filename = re.sub(r'\s+', '_', filename)
    
    return filename


def calculate_percentage(part, total):
    """
    Tính phần trăm
    
    Args:
        part: Phần
        total: Tổng
    
    Returns:
        float: Phần trăm (0-100)
    """
    if not total or total == 0:
        return 0.0
    
    percentage = (part / total) * 100
    return round(percentage, 2)


def get_timestamp():
    """
    Lấy timestamp hiện tại
    
    Returns:
        str: Timestamp ISO format
    """
    return datetime.utcnow().isoformat()


def parse_timestamp(timestamp_str):
    """
    Parse timestamp string
    
    Args:
        timestamp_str: Timestamp string
    
    Returns:
        datetime: Datetime object
    """
    try:
        return datetime.fromisoformat(timestamp_str)
    except Exception:
        return None


def format_file_size(bytes_size):
    """
    Format kích thước file
    
    Args:
        bytes_size: Kích thước (bytes)
    
    Returns:
        str: Kích thước dễ đọc
    """
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"


def truncate_text(text, max_length=100, suffix='...'):
    """
    Cắt ngắn text
    
    Args:
        text: Text cần cắt
        max_length: Độ dài tối đa
        suffix: Hậu tố khi cắt
    
    Returns:
        str: Text đã cắt
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def slugify(text):
    """
    Chuyển text thành slug
    
    Args:
        text: Text cần chuyển
    
    Returns:
        str: Slug
    """
    # Chuyển về lowercase
    text = text.lower()
    
    # Loại bỏ ký tự đặc biệt
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Thay thế khoảng trắng bằng dấu gạch ngang
    text = re.sub(r'[\s_]+', '-', text)
    
    # Loại bỏ dấu gạch ngang thừa
    text = re.sub(r'^-+|-+$', '', text)
    
    return text


def is_valid_url(url):
    """
    Kiểm tra URL hợp lệ
    
    Args:
        url: URL cần kiểm tra
    
    Returns:
        bool: True nếu URL hợp lệ
    """
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def extract_youtube_video_id(url):
    """
    Trích xuất video ID từ YouTube URL
    
    Args:
        url: YouTube URL
    
    Returns:
        str: Video ID hoặc None
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def clean_text(text):
    """
    Làm sạch text
    
    Args:
        text: Text cần làm sạch
    
    Returns:
        str: Text đã làm sạch
    """
    if not text:
        return ""
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    return text


def parse_srt_time(time_str):
    """
    Parse SRT timestamp
    
    Args:
        time_str: Timestamp string (00:00:00,000)
    
    Returns:
        float: Số giây
    """
    try:
        # Format: 00:00:00,000
        time_parts = time_str.replace(',', '.').split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = float(time_parts[2])
        
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    except Exception:
        return 0.0


def format_srt_time(seconds):
    """
    Format giây thành SRT timestamp
    
    Args:
        seconds: Số giây
    
    Returns:
        str: SRT timestamp (00:00:00,000)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"