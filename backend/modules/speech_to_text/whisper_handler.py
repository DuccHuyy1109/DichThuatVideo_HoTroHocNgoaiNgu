"""
Whisper Handler
Xử lý Speech-to-Text bằng Faster-Whisper và WhisperX
"""
import logging
import os
from faster_whisper import WhisperModel
from config import Config

logger = logging.getLogger(__name__)

# Global model instance (lazy loading)
_whisper_model = None


def get_whisper_model():
    """
    Lấy Whisper model instance (singleton pattern)
    
    Returns:
        WhisperModel instance
    """
    global _whisper_model
    
    if _whisper_model is None:
        logger.info(f"Loading Whisper model: {Config.WHISPER_MODEL}")
        _whisper_model = WhisperModel(
            Config.WHISPER_MODEL,
            device=Config.WHISPER_DEVICE,
            compute_type=Config.WHISPER_COMPUTE_TYPE
        )
        logger.info("Whisper model loaded successfully")
    
    return _whisper_model


def transcribe_audio_whisper(audio_path, language=None):
    """
    Chuyển audio thành text bằng Faster-Whisper
    
    Args:
        audio_path: Đường dẫn audio file
        language: Mã ngôn ngữ (None = auto detect)
    
    Returns:
        tuple: (success: bool, result: dict, message: str)
        result = {
            'text': str,
            'segments': list,
            'language': str
        }
    """
    try:
        # Kiểm tra file tồn tại
        if not os.path.exists(audio_path):
            return False, None, "File audio không tồn tại"
        
        logger.info(f"Bắt đầu transcribe audio: {audio_path}")
        
        # Lấy model
        model = get_whisper_model()
        
        # Transcribe
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,  # Voice Activity Detection
            word_timestamps=True  # Lấy timestamp cho từng từ
        )
        
        # Xử lý kết quả
        full_text = ""
        segments_list = []
        
        for segment in segments:
            full_text += segment.text + " "
            
            segment_dict = {
                'id': segment.id,
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
                'words': []
            }
            
            # Thêm word-level timestamps nếu có
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    segment_dict['words'].append({
                        'word': word.word,
                        'start': word.start,
                        'end': word.end,
                        'probability': word.probability
                    })
            
            segments_list.append(segment_dict)
        
        result = {
            'text': full_text.strip(),
            'segments': segments_list,
            'language': info.language,
            'language_probability': info.language_probability,
            'duration': info.duration
        }
        
        logger.info(f"Transcribe hoàn tất. Ngôn ngữ: {info.language}")
        
        return True, result, "Transcribe thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi transcribe: {str(e)}")
        return False, None, f"Lỗi khi transcribe: {str(e)}"


def transcribe_audio_with_alignment(audio_path, language=None):
    """
    Transcribe audio với alignment tốt hơn (sử dụng WhisperX nếu cần)
    
    Args:
        audio_path: Đường dẫn audio
        language: Mã ngôn ngữ
    
    Returns:
        tuple: (success: bool, result: dict, message: str)
    """
    try:
        # Sử dụng Faster-Whisper trước
        success, result, message = transcribe_audio_whisper(audio_path, language)
        
        if not success:
            return False, None, message
        
        # TODO: Có thể thêm WhisperX để cải thiện alignment
        # import whisperx
        # ...
        
        return True, result, "Transcribe với alignment thành công"
        
    except Exception as e:
        logger.error(f"Lỗi transcribe with alignment: {str(e)}")
        return False, None, f"Lỗi: {str(e)}"


def get_transcript_with_timestamps(audio_path, language=None):
    """
    Lấy transcript với timestamps chi tiết
    
    Args:
        audio_path: Đường dẫn audio
        language: Mã ngôn ngữ
    
    Returns:
        list: Danh sách segments với timestamps
    """
    try:
        success, result, message = transcribe_audio_whisper(audio_path, language)
        
        if not success:
            return []
        
        return result['segments']
        
    except Exception as e:
        logger.error(f"Lỗi get transcript: {str(e)}")
        return []