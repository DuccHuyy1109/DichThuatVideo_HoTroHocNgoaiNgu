"""
Language Detector
Phát hiện ngôn ngữ từ text hoặc audio
"""
import logging
from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)


def detect_language(text):
    """
    Phát hiện ngôn ngữ từ text
    
    Args:
        text: Text cần phát hiện
    
    Returns:
        tuple: (language_code: str, probability: float)
    """
    try:
        if not text or len(text.strip()) < 10:
            return None, 0.0
        
        # Detect language
        language = detect(text)
        
        # Lấy probability
        langs = detect_langs(text)
        probability = 0.0
        
        for lang in langs:
            if lang.lang == language:
                probability = lang.prob
                break
        
        logger.info(f"Detected language: {language} (probability: {probability:.2f})")
        
        return language, probability
        
    except LangDetectException as e:
        logger.warning(f"Không thể phát hiện ngôn ngữ: {str(e)}")
        return None, 0.0
    except Exception as e:
        logger.error(f"Lỗi khi phát hiện ngôn ngữ: {str(e)}")
        return None, 0.0


def detect_language_from_audio_result(transcription_result):
    """
    Lấy ngôn ngữ từ kết quả transcription
    
    Args:
        transcription_result: Kết quả từ Whisper
    
    Returns:
        str: Mã ngôn ngữ
    """
    try:
        if transcription_result and 'language' in transcription_result:
            return transcription_result['language']
        
        return None
        
    except Exception as e:
        logger.error(f"Lỗi lấy language: {str(e)}")
        return None


def is_language_supported(language_code, supported_languages):
    """
    Kiểm tra ngôn ngữ có được hỗ trợ không
    
    Args:
        language_code: Mã ngôn ngữ
        supported_languages: List các ngôn ngữ được hỗ trợ
    
    Returns:
        bool: True nếu được hỗ trợ
    """
    return language_code in supported_languages


def get_language_name(language_code):
    """
    Lấy tên ngôn ngữ từ mã
    
    Args:
        language_code: Mã ngôn ngữ (en, vi, ja, ...)
    
    Returns:
        str: Tên ngôn ngữ
    """
    language_names = {
        'en': 'English',
        'vi': 'Tiếng Việt',
        'ja': '日本語',
        'ko': '한국어',
        'zh': '中文',
        'fr': 'Français',
        'de': 'Deutsch',
        'es': 'Español',
        'pt': 'Português',
        'ru': 'Русский',
        'ar': 'العربية',
        'hi': 'हिन्दी',
        'th': 'ไทย',
        'id': 'Bahasa Indonesia'
    }
    
    return language_names.get(language_code, language_code.upper())