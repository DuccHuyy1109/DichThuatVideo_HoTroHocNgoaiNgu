"""
Timestamp Synchronization
Đồng bộ và điều chỉnh timestamps
"""
import logging

logger = logging.getLogger(__name__)


def sync_timestamps(segments, video_duration):
    """
    Đồng bộ timestamps với video duration
    
    Args:
        segments: List segments
        video_duration: Thời lượng video (giây)
    
    Returns:
        list: Segments đã sync
    """
    try:
        if not segments:
            return []
        
        synced_segments = []
        
        for segment in segments:
            # Kiểm tra timestamps hợp lệ
            if segment['start'] >= video_duration:
                continue
            
            if segment['end'] > video_duration:
                segment['end'] = video_duration
            
            synced_segments.append(segment)
        
        return synced_segments
        
    except Exception as e:
        logger.error(f"Lỗi sync timestamps: {str(e)}")
        return segments


def adjust_timestamps(segments, offset=0.0):
    """
    Điều chỉnh timestamps với offset
    
    Args:
        segments: List segments
        offset: Offset (giây, có thể âm hoặc dương)
    
    Returns:
        list: Segments đã điều chỉnh
    """
    try:
        adjusted = []
        
        for segment in segments:
            adj_segment = segment.copy()
            adj_segment['start'] = max(0, segment['start'] + offset)
            adj_segment['end'] = max(0, segment['end'] + offset)
            adjusted.append(adj_segment)
        
        return adjusted
        
    except Exception as e:
        logger.error(f"Lỗi adjust timestamps: {str(e)}")
        return segments


def fix_overlapping_timestamps(segments):
    """
    Sửa các timestamps bị chồng lấp
    
    Args:
        segments: List segments
    
    Returns:
        list: Segments đã sửa
    """
    try:
        if not segments:
            return []
        
        fixed = [segments[0].copy()]
        
        for i in range(1, len(segments)):
            current = segments[i].copy()
            previous = fixed[-1]
            
            # Nếu start time của current <= end time của previous
            if current['start'] <= previous['end']:
                # Điều chỉnh
                gap = 0.1  # 100ms gap
                current['start'] = previous['end'] + gap
                
                # Đảm bảo end > start
                if current['end'] <= current['start']:
                    current['end'] = current['start'] + 1.0
            
            fixed.append(current)
        
        return fixed
        
    except Exception as e:
        logger.error(f"Lỗi fix overlapping: {str(e)}")
        return segments


def validate_timestamps(segments):
    """
    Kiểm tra tính hợp lệ của timestamps
    
    Args:
        segments: List segments
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    errors = []
    
    for i, segment in enumerate(segments):
        # Kiểm tra start < end
        if segment['start'] >= segment['end']:
            errors.append(f"Segment {i}: start >= end")
        
        # Kiểm tra timestamps không âm
        if segment['start'] < 0 or segment['end'] < 0:
            errors.append(f"Segment {i}: timestamp âm")
        
        # Kiểm tra chồng lấp
        if i > 0:
            prev_segment = segments[i-1]
            if segment['start'] < prev_segment['end']:
                errors.append(f"Segment {i}: chồng lấp với segment {i-1}")
    
    is_valid = len(errors) == 0
    
    return is_valid, errors