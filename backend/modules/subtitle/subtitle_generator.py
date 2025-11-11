"""
Subtitle Generator
Tạo file phụ đề SRT/VTT
"""
import logging
import os
from utils.helpers import format_srt_time

logger = logging.getLogger(__name__)


def generate_subtitle_file(segments, output_path, subtitle_format='srt'):
    """
    Tạo file phụ đề từ segments
    
    Args:
        segments: List các segments với timestamps
        output_path: Đường dẫn lưu file
        subtitle_format: Format (srt hoặc vtt)
    
    Returns:
        tuple: (success: bool, file_path: str, message: str)
    """
    try:
        if not segments:
            return False, None, "Không có segments để tạo phụ đề"
        
        # Tạo thư mục nếu chưa có
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if subtitle_format.lower() == 'srt':
            success = create_srt_file(segments, output_path)
        elif subtitle_format.lower() == 'vtt':
            success = create_vtt_file(segments, output_path)
        else:
            return False, None, f"Format không được hỗ trợ: {subtitle_format}"
        
        if success:
            logger.info(f"Tạo file phụ đề thành công: {output_path}")
            return True, output_path, "Tạo phụ đề thành công"
        else:
            return False, None, "Lỗi khi tạo file phụ đề"
        
    except Exception as e:
        logger.error(f"Lỗi tạo file phụ đề: {str(e)}")
        return False, None, f"Lỗi: {str(e)}"


def create_srt_file(segments, output_path):
    """
    Tạo file SRT
    
    Args:
        segments: List segments
        output_path: Đường dẫn file
    
    Returns:
        bool: True nếu thành công
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                # Số thứ tự
                f.write(f"{i}\n")
                
                # Timestamps
                start_time = format_srt_time(segment['start'])
                end_time = format_srt_time(segment['end'])
                f.write(f"{start_time} --> {end_time}\n")
                
                # Text
                f.write(f"{segment['text']}\n")
                
                # Dòng trống
                f.write("\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Lỗi tạo SRT: {str(e)}")
        return False


def create_vtt_file(segments, output_path):
    """
    Tạo file VTT
    
    Args:
        segments: List segments
        output_path: Đường dẫn file
    
    Returns:
        bool: True nếu thành công
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("WEBVTT\n\n")
            
            for i, segment in enumerate(segments, 1):
                # Timestamps (VTT sử dụng dấu chấm thay vì dấu phẩy)
                start_time = format_srt_time(segment['start']).replace(',', '.')
                end_time = format_srt_time(segment['end']).replace(',', '.')
                f.write(f"{start_time} --> {end_time}\n")
                
                # Text
                f.write(f"{segment['text']}\n")
                
                # Dòng trống
                f.write("\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Lỗi tạo VTT: {str(e)}")
        return False


def create_bilingual_subtitle(segments, output_path, subtitle_format='srt'):
    """
    Tạo phụ đề song ngữ
    
    Args:
        segments: List segments có cả text và translation
        output_path: Đường dẫn file
        subtitle_format: Format (srt hoặc vtt)
    
    Returns:
        tuple: (success: bool, file_path: str, message: str)
    """
    try:
        if not segments:
            return False, None, "Không có segments"
        
        # Tạo thư mục
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if subtitle_format.lower() == 'srt':
            success = create_bilingual_srt(segments, output_path)
        elif subtitle_format.lower() == 'vtt':
            success = create_bilingual_vtt(segments, output_path)
        else:
            return False, None, f"Format không hỗ trợ: {subtitle_format}"
        
        if success:
            logger.info(f"Tạo phụ đề song ngữ thành công: {output_path}")
            return True, output_path, "Tạo phụ đề song ngữ thành công"
        else:
            return False, None, "Lỗi khi tạo phụ đề song ngữ"
        
    except Exception as e:
        logger.error(f"Lỗi tạo phụ đề song ngữ: {str(e)}")
        return False, None, f"Lỗi: {str(e)}"


def create_bilingual_srt(segments, output_path):
    """
    Tạo file SRT song ngữ
    
    Args:
        segments: List segments có text và translation
        output_path: Đường dẫn file
    
    Returns:
        bool: True nếu thành công
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                # Số thứ tự
                f.write(f"{i}\n")
                
                # Timestamps
                start_time = format_srt_time(segment['start'])
                end_time = format_srt_time(segment['end'])
                f.write(f"{start_time} --> {end_time}\n")
                
                # Text gốc
                f.write(f"{segment['text']}\n")
                
                # Translation (nếu có)
                if 'translation' in segment and segment['translation']:
                    f.write(f"{segment['translation']}\n")
                
                # Dòng trống
                f.write("\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Lỗi tạo bilingual SRT: {str(e)}")
        return False


def create_bilingual_vtt(segments, output_path):
    """
    Tạo file VTT song ngữ
    
    Args:
        segments: List segments
        output_path: Đường dẫn file
    
    Returns:
        bool: True nếu thành công
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("WEBVTT\n\n")
            
            for i, segment in enumerate(segments, 1):
                # Timestamps
                start_time = format_srt_time(segment['start']).replace(',', '.')
                end_time = format_srt_time(segment['end']).replace(',', '.')
                f.write(f"{start_time} --> {end_time}\n")
                
                # Text gốc
                f.write(f"{segment['text']}\n")
                
                # Translation
                if 'translation' in segment and segment['translation']:
                    f.write(f"{segment['translation']}\n")
                
                # Dòng trống
                f.write("\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Lỗi tạo bilingual VTT: {str(e)}")
        return False


def merge_short_segments(segments, min_duration=1.0, max_duration=7.0):
    """
    Gộp các segments ngắn lại
    
    Args:
        segments: List segments
        min_duration: Thời lượng tối thiểu
        max_duration: Thời lượng tối đa
    
    Returns:
        list: Segments đã được gộp
    """
    try:
        if not segments:
            return []
        
        merged = []
        current = None
        
        for segment in segments:
            duration = segment['end'] - segment['start']
            
            if current is None:
                current = segment.copy()
            elif (current['end'] - current['start']) < max_duration:
                # Gộp vào current
                current['end'] = segment['end']
                current['text'] += " " + segment['text']
                if 'translation' in segment:
                    current['translation'] = current.get('translation', '') + " " + segment['translation']
            else:
                merged.append(current)
                current = segment.copy()
        
        if current:
            merged.append(current)
        
        return merged
        
    except Exception as e:
        logger.error(f"Lỗi merge segments: {str(e)}")
        return segments