"""
Audio Extractor
Trích xuất audio từ video
"""
import logging
import os
from moviepy import VideoFileClip
from config import Config

logger = logging.getLogger(__name__)


def extract_audio_from_video(video_path, output_path=None):
    """
    Trích xuất audio từ video
    
    Args:
        video_path: Đường dẫn video
        output_path: Đường dẫn lưu audio (optional)
    
    Returns:
        tuple: (success: bool, audio_path: str, message: str)
    """
    try:
        # Kiểm tra video tồn tại
        if not os.path.exists(video_path):
            return False, None, "File video không tồn tại"
        
        # Tạo output path nếu không có
        if not output_path:
            video_filename = os.path.basename(video_path)
            video_name = os.path.splitext(video_filename)[0]
            output_path = os.path.join(
                Config.AUDIO_FOLDER,
                f"{video_name}.wav"
            )
        
        # Tạo thư mục nếu chưa có
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Load video
        logger.info(f"Đang trích xuất audio từ: {video_path}")
        video = VideoFileClip(video_path)
        
        # Kiểm tra có audio không
        if video.audio is None:
            video.close()
            return False, None, "Video không có audio"
        
        # Trích xuất audio
        audio = video.audio
        audio.write_audiofile(
            output_path,
            codec='pcm_s16le',  # WAV format
            fps=16000,  # Sample rate 16kHz cho Whisper
            nbytes=2,
            buffersize=2000,
            logger=None  # Tắt logging của moviepy
        )
        
        # Đóng video
        video.close()
        
        logger.info(f"Audio đã được trích xuất: {output_path}")
        
        return True, output_path, "Trích xuất audio thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi trích xuất audio: {str(e)}")
        return False, None, f"Lỗi khi trích xuất audio: {str(e)}"


def extract_audio_segment(video_path, start_time, end_time, output_path=None):
    """
    Trích xuất một đoạn audio từ video
    
    Args:
        video_path: Đường dẫn video
        start_time: Thời gian bắt đầu (giây)
        end_time: Thời gian kết thúc (giây)
        output_path: Đường dẫn lưu audio (optional)
    
    Returns:
        tuple: (success: bool, audio_path: str, message: str)
    """
    try:
        # Kiểm tra video tồn tại
        if not os.path.exists(video_path):
            return False, None, "File video không tồn tại"
        
        # Tạo output path nếu không có
        if not output_path:
            video_filename = os.path.basename(video_path)
            video_name = os.path.splitext(video_filename)[0]
            output_path = os.path.join(
                Config.AUDIO_FOLDER,
                f"{video_name}_segment_{start_time}_{end_time}.wav"
            )
        
        # Tạo thư mục nếu chưa có
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Load video và cắt segment
        video = VideoFileClip(video_path).subclip(start_time, end_time)
        
        # Kiểm tra có audio không
        if video.audio is None:
            video.close()
            return False, None, "Video không có audio"
        
        # Trích xuất audio
        audio = video.audio
        audio.write_audiofile(
            output_path,
            codec='pcm_s16le',
            fps=16000,
            nbytes=2,
            buffersize=2000,
            logger=None
        )
        
        # Đóng video
        video.close()
        
        logger.info(f"Audio segment đã được trích xuất: {output_path}")
        
        return True, output_path, "Trích xuất audio segment thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi trích xuất audio segment: {str(e)}")
        return False, None, f"Lỗi: {str(e)}"


def get_audio_info(audio_path):
    """
    Lấy thông tin audio
    
    Args:
        audio_path: Đường dẫn audio
    
    Returns:
        dict: Thông tin audio
    """
    try:
        from pydub import AudioSegment
        
        audio = AudioSegment.from_file(audio_path)
        
        info = {
            'duration': len(audio) / 1000.0,  # chuyển ms sang giây
            'channels': audio.channels,
            'sample_rate': audio.frame_rate,
            'sample_width': audio.sample_width,
            'size': os.path.getsize(audio_path)
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin audio: {str(e)}")
        return None