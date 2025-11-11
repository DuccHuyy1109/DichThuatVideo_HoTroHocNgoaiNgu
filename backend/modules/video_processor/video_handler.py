"""
Video Handler
Xử lý và validate video
"""
import logging
import os
from moviepy import VideoFileClip  # ✅ Cách mới
from utils.validators import validate_duration
from config import Config

logger = logging.getLogger(__name__)


def get_video_info(video_path):
    """
    Lấy thông tin video
    
    Args:
        video_path: Đường dẫn video
    
    Returns:
        dict: Thông tin video (duration, fps, size, resolution)
    """
    try:
        if not os.path.exists(video_path):
            return None
        
        # Load video
        video = VideoFileClip(video_path)
        
        info = {
            'duration': video.duration,  # giây
            'fps': video.fps,
            'size': os.path.getsize(video_path),  # bytes
            'resolution': (video.w, video.h),
            'has_audio': video.audio is not None
        }
        
        # Đóng video
        video.close()
        
        logger.info(f"Video info: {info}")
        
        return info
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin video: {str(e)}")
        return None


def validate_video(video_path):
    """
    Validate video
    
    Args:
        video_path: Đường dẫn video
    
    Returns:
        tuple: (is_valid: bool, message: str, info: dict)
    """
    try:
        # Kiểm tra file tồn tại
        if not os.path.exists(video_path):
            return False, "File video không tồn tại", None
        
        # Lấy thông tin video
        info = get_video_info(video_path)
        
        if not info:
            return False, "Không thể đọc thông tin video", None
        
        # Validate duration
        is_valid, message = validate_duration(
            info['duration'],
            Config.MAX_VIDEO_DURATION
        )
        
        if not is_valid:
            return False, message, info
        
        # Kiểm tra có audio không
        if not info['has_audio']:
            return False, "Video không có audio", info
        
        return True, "Video hợp lệ", info
        
    except Exception as e:
        logger.error(f"Lỗi khi validate video: {str(e)}")
        return False, f"Lỗi khi validate video: {str(e)}", None


def get_video_duration(video_path):
    """
    Lấy thời lượng video
    
    Args:
        video_path: Đường dẫn video
    
    Returns:
        float: Thời lượng (giây)
    """
    try:
        video = VideoFileClip(video_path)
        duration = video.duration
        video.close()
        return duration
    except Exception as e:
        logger.error(f"Lỗi khi lấy duration: {str(e)}")
        return 0


def check_video_format(video_path):
    """
    Kiểm tra format video
    
    Args:
        video_path: Đường dẫn video
    
    Returns:
        bool: True nếu format hợp lệ
    """
    try:
        video = VideoFileClip(video_path)
        video.close()
        return True
    except Exception as e:
        logger.error(f"Format video không hợp lệ: {str(e)}")
        return False