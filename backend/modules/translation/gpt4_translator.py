"""
GPT-4 Translator
Dịch văn bản sử dụng GPT-4o với ngữ cảnh
"""
import logging
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)


def translate_text_gpt4(text, source_language='en', target_language='vi', context=None):
    """
    Dịch văn bản sử dụng GPT-4o
    
    Args:
        text: Văn bản cần dịch
        source_language: Ngôn ngữ nguồn
        target_language: Ngôn ngữ đích
        context: Ngữ cảnh bổ sung
    
    Returns:
        tuple: (success: bool, translation: str, message: str)
    """
    try:
        if not text or not text.strip():
            return False, None, "Văn bản trống"
        
        # Tạo prompt
        prompt = create_translation_prompt(text, source_language, target_language, context)
        
        logger.info(f"Đang dịch văn bản từ {source_language} sang {target_language}")
        
        # Gọi GPT-4o API
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là một chuyên gia dịch thuật chuyên nghiệp. Hãy dịch chính xác và tự nhiên, giữ nguyên ý nghĩa và ngữ cảnh của câu gốc."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Lấy kết quả
        translation = response.choices[0].message.content.strip()
        
        logger.info("Dịch thành công")
        
        return True, translation, "Dịch thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi dịch: {str(e)}")
        return False, None, f"Lỗi khi dịch: {str(e)}"


def translate_segments_gpt4(segments, source_language='en', target_language='vi'):
    """
    Dịch nhiều segments với ngữ cảnh
    
    Args:
        segments: List các segments cần dịch
        source_language: Ngôn ngữ nguồn
        target_language: Ngôn ngữ đích
    
    Returns:
        tuple: (success: bool, translated_segments: list, message: str)
    """
    try:
        if not segments:
            return False, None, "Không có segments để dịch"
        
        translated_segments = []
        
        # Dịch theo batch để có ngữ cảnh tốt hơn
        batch_size = 10
        
        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            
            # Tạo context từ các segments trước và sau
            context_before = segments[max(0, i-2):i] if i > 0 else []
            context_after = segments[i+batch_size:i+batch_size+2] if i+batch_size < len(segments) else []
            
            # Dịch batch
            success, batch_translations = translate_batch_with_context(
                batch, context_before, context_after, 
                source_language, target_language
            )
            
            if not success:
                logger.warning(f"Lỗi dịch batch {i}")
                continue
            
            translated_segments.extend(batch_translations)
        
        logger.info(f"Đã dịch {len(translated_segments)} segments")
        
        return True, translated_segments, "Dịch segments thành công"
        
    except Exception as e:
        logger.error(f"Lỗi khi dịch segments: {str(e)}")
        return False, None, f"Lỗi: {str(e)}"


def translate_batch_with_context(batch, context_before, context_after, source_language, target_language):
    """
    Dịch một batch segments với ngữ cảnh
    
    Args:
        batch: List segments cần dịch
        context_before: Ngữ cảnh trước
        context_after: Ngữ cảnh sau
        source_language: Ngôn ngữ nguồn
        target_language: Ngôn ngữ đích
    
    Returns:
        tuple: (success: bool, translations: list)
    """
    try:
        # Tạo text từ batch
        batch_texts = [seg['text'] for seg in batch]
        combined_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(batch_texts)])
        
        # Tạo context
        context_text = ""
        if context_before:
            context_text += "Ngữ cảnh trước:\n"
            context_text += "\n".join([seg['text'] for seg in context_before])
            context_text += "\n\n"
        
        # Tạo prompt
        prompt = f"""Dịch các câu sau từ {get_language_name(source_language)} sang {get_language_name(target_language)}.
Giữ nguyên số thứ tự và dịch từng câu một cách chính xác, tự nhiên.

{context_text}Văn bản cần dịch:
{combined_text}

Chỉ trả về bản dịch, giữ nguyên định dạng số thứ tự."""
        
        # Gọi GPT-4o
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia dịch thuật. Dịch chính xác và tự nhiên, phù hợp với ngữ cảnh."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        # Parse kết quả
        translation_text = response.choices[0].message.content.strip()
        translations = parse_batch_translation(translation_text, batch)
        
        return True, translations
        
    except Exception as e:
        logger.error(f"Lỗi dịch batch: {str(e)}")
        return False, []


def parse_batch_translation(translation_text, original_batch):
    """
    Parse kết quả dịch batch
    
    Args:
        translation_text: Text đã dịch
        original_batch: Batch gốc
    
    Returns:
        list: Danh sách segments đã dịch
    """
    try:
        translations = []
        lines = translation_text.split('\n')
        
        for i, segment in enumerate(original_batch):
            # Tìm dòng tương ứng
            translation = None
            for line in lines:
                if line.strip().startswith(f"{i+1}."):
                    translation = line.strip()[len(f"{i+1}."):].strip()
                    break
            
            # Nếu không tìm thấy, dùng text gốc
            if not translation:
                translation = segment['text']
            
            translated_segment = segment.copy()
            translated_segment['translation'] = translation
            translations.append(translated_segment)
        
        return translations
        
    except Exception as e:
        logger.error(f"Lỗi parse translation: {str(e)}")
        return []


def create_translation_prompt(text, source_language, target_language, context=None):
    """
    Tạo prompt cho dịch thuật
    
    Args:
        text: Văn bản cần dịch
        source_language: Ngôn ngữ nguồn
        target_language: Ngôn ngữ đích
        context: Ngữ cảnh
    
    Returns:
        str: Prompt
    """
    prompt = f"Dịch văn bản sau từ {get_language_name(source_language)} sang {get_language_name(target_language)}:\n\n"
    
    if context:
        prompt += f"Ngữ cảnh: {context}\n\n"
    
    prompt += f"Văn bản: {text}\n\n"
    prompt += "Chỉ trả về bản dịch, không thêm giải thích."
    
    return prompt


def get_language_name(language_code):
    """
    Lấy tên ngôn ngữ từ mã
    
    Args:
        language_code: Mã ngôn ngữ
    
    Returns:
        str: Tên ngôn ngữ
    """
    names = {
        'en': 'tiếng Anh',
        'vi': 'tiếng Việt',
        'ja': 'tiếng Nhật',
        'ko': 'tiếng Hàn',
        'zh': 'tiếng Trung',
        'fr': 'tiếng Pháp',
        'de': 'tiếng Đức',
        'es': 'tiếng Tây Ban Nha'
    }
    return names.get(language_code, language_code)