"""
Vocabulary Extraction Module - ULTIMATE COMPLETE VERSION
Trích xuất từ vựng từ transcript với GPT-4 - Đầy đủ và robust nhất

Features:
- ✅ Extract đúng ngôn ngữ (ko, en, ja, etc.)
- ✅ Retry logic (3 attempts)
- ✅ Anti-truncation (dynamic max_words)
- ✅ Multiple extraction methods
- ✅ Complete validation & cleaning
"""
import logging
import json
import time
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=Config.OPENAI_API_KEY)


def extract_vocabulary_from_transcript(segments, video_language, max_words=15):
    """
    ✅ ULTIMATE: Trích xuất từ vựng ĐÚNG ngôn ngữ với anti-truncation
    
    Args:
        segments: List of transcript segments
        video_language: Language code (en, ko, ja, etc.)
        max_words: Number of vocabulary words (default: 15, max: 20)
    
    Returns:
        tuple: (success: bool, vocabularies: list, message: str)
    """
    try:
        if not segments or len(segments) == 0:
            return False, [], "Không có segments để trích xuất"
        
        # Ghép text từ segments (limit 50 để tránh quá dài)
        full_text = " ".join([seg.get('text', '') for seg in segments[:50]])
        
        if not full_text.strip():
            return False, [], "Text rỗng"
        
        logger.info(f"📚 Extracting {max_words} vocabularies for language: {video_language}")
        logger.info(f"📝 Text length: {len(full_text)} characters")
        
        # ✅ CRITICAL: Prompt chỉ định RÕ ngôn ngữ
        prompt = f"""Bạn là chuyên gia ngôn ngữ {video_language.upper()}.

Trích xuất {max_words} từ vựng QUAN TRỌNG NHẤT từ văn bản {video_language.upper()} sau:

{full_text}

YÊU CẦU QUAN TRỌNG:
1. CHỈ trích xuất từ {video_language.upper()} (KHÔNG dùng tiếng Anh nếu đây không phải video tiếng Anh)
2. Word phải là từ {video_language.upper()} gốc
3. Pronunciation là IPA hoặc romanization của {video_language.upper()}
4. Example sentence phải bằng {video_language.upper()}
5. Giữ response NGẮN GỌN để tránh bị cắt

Ví dụ với tiếng Hàn:
{{
  "word": "감사합니다",
  "translation": "cảm ơn",
  "pronunciation": "[gam-sa-ham-ni-da]",
  "part_of_speech": "expression",
  "example_sentence": "정말 감사합니다!",
  "example_translation": "Thật sự cảm ơn!",
  "difficulty_level": "basic"
}}

Trả về JSON array (KHÔNG markdown, KHÔNG ```):
[
  {{
    "word": "từ gốc",
    "translation": "nghĩa tiếng Việt",
    "pronunciation": "phiên âm/romanization",
    "part_of_speech": "noun/verb/adjective/phrase",
    "example_sentence": "câu ví dụ ngắn",
    "example_translation": "dịch câu ví dụ",
    "difficulty_level": "basic/intermediate/advanced"
  }}
]"""

        # Retry logic với dynamic max_words
        max_retries = 3
        current_max_words = max_words
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 GPT-4 attempt {attempt + 1}/{max_retries} (requesting {current_max_words} words)...")
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a {video_language} vocabulary expert. Return valid JSON array. Keep responses CONCISE. Each string must be complete and properly closed."
                        },
                        {
                            "role": "user",
                            "content": prompt.replace(str(max_words), str(current_max_words))  # Update count
                        }
                    ],
                    temperature=0.2,  # Low temp for consistency
                    max_tokens=10000,  # High enough to avoid truncation
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content.strip()
                finish_reason = response.choices[0].finish_reason
                
                logger.info(f"📥 GPT-4 response: {len(content)} chars, finish_reason: {finish_reason}")
                
                # ✅ CHECK: Response có bị truncate không?
                if finish_reason == 'length':
                    logger.warning(f"⚠️ Response truncated! Reducing word count...")
                    if attempt < max_retries - 1:
                        current_max_words = max(8, current_max_words - 5)
                        logger.info(f"🔄 Retrying with {current_max_words} words")
                        time.sleep(1)
                        continue
                
                # Clean markdown nếu có
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                try:
                    data = json.loads(content)
                    
                    # Extract array từ object
                    if isinstance(data, dict):
                        # Thử các keys phổ biến
                        for key in ['vocabularies', 'words', 'vocabulary', 'items', 'data']:
                            if key in data and isinstance(data[key], list):
                                vocabularies = data[key]
                                break
                        else:
                            # Lấy giá trị list đầu tiên
                            for value in data.values():
                                if isinstance(value, list):
                                    vocabularies = value
                                    break
                            else:
                                raise ValueError("No array found in response")
                    elif isinstance(data, list):
                        vocabularies = data
                    else:
                        raise ValueError("Invalid response format")
                    
                    logger.info(f"✅ Parsed {len(vocabularies)} vocabularies successfully")
                    break  # Success! Exit retry loop
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Attempt {attempt + 1} - JSON parse error: {str(e)}")
                    logger.warning(f"Content preview: {content[:300]}...")
                    
                    # ✅ CHECK: Có phải do truncation không?
                    if "Unterminated string" in str(e) or "Expecting" in str(e):
                        logger.warning(f"⚠️ Likely truncation issue, reducing word count...")
                        if attempt < max_retries - 1:
                            current_max_words = max(8, current_max_words - 5)
                            logger.info(f"🔄 Retrying with {current_max_words} words")
                            time.sleep(1)
                            continue
                    
                    if attempt == max_retries - 1:
                        return False, [], f"JSON parse error after {max_retries} attempts: {str(e)}"
                    
                    time.sleep(1)
                    continue
                    
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} - API error: {str(e)}")
                
                if attempt == max_retries - 1:
                    return False, [], f"API error after {max_retries} attempts: {str(e)}"
                
                time.sleep(1)
                continue
        
        # ✅ Validate và clean data
        cleaned_vocabularies = []
        
        for idx, vocab in enumerate(vocabularies):
            try:
                # Required fields
                word = str(vocab.get('word', '')).strip()
                translation = str(vocab.get('translation', '')).strip()
                
                # Skip nếu thiếu thông tin quan trọng
                if not word or not translation:
                    logger.warning(f"⚠️ Skipping vocab {idx + 1}: missing word or translation")
                    continue
                
                # Skip nếu có ký tự lỗi
                if '???' in word or '???' in translation:
                    logger.warning(f"⚠️ Skipping vocab {idx + 1}: contains ???")
                    continue
                
                # Clean và build vocab object
                cleaned_vocab = {
                    'word': word,
                    'translation': translation,
                    'pronunciation': str(vocab.get('pronunciation', '')).strip() or f"[{word}]",
                    'part_of_speech': str(vocab.get('part_of_speech', 'word')).strip(),
                    'example_sentence': str(vocab.get('example_sentence', '')).strip(),
                    'example_translation': str(vocab.get('example_translation', '')).strip(),
                    'difficulty_level': str(vocab.get('difficulty_level', 'intermediate')).strip()
                }
                
                # Fix pronunciation nếu bị rỗng hoặc N/A
                if cleaned_vocab['pronunciation'] in ['N/A', '', '???']:
                    cleaned_vocab['pronunciation'] = f"[{word}]"
                
                cleaned_vocabularies.append(cleaned_vocab)
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing vocab {idx + 1}: {str(e)}")
                continue
        
        if len(cleaned_vocabularies) == 0:
            return False, [], "Không trích xuất được từ vựng hợp lệ"
        
        logger.info(f"✅ Successfully extracted {len(cleaned_vocabularies)} valid vocabularies for language {video_language}")
        
        return True, cleaned_vocabularies, "Trích xuất thành công"
        
    except Exception as e:
        logger.error(f"❌ Fatal error in vocabulary extraction: {str(e)}", exc_info=True)
        return False, [], f"Lỗi trích xuất: {str(e)}"


def save_vocabulary_to_database(vocabularies, language, video_id, db):
    """
    ✅ COMPLETE: Lưu vocabularies vào database với video_id
    
    Args:
        vocabularies: List of vocabulary dicts
        language: Language code (en, ko, ja, etc.)
        video_id: Video ID to link to (CRITICAL!)
        db: Database session
    
    Returns:
        tuple: (success: bool, vocab_ids: list, message: str)
    """
    try:
        from database.models import Vocabulary
        
        if not vocabularies or len(vocabularies) == 0:
            return False, [], "Danh sách từ vựng rỗng"
        
        vocab_ids = []
        
        logger.info(f"💾 Saving {len(vocabularies)} vocabularies for video {video_id}...")
        
        for idx, vocab in enumerate(vocabularies):
            try:
                new_vocab = Vocabulary(
                    video_id=video_id,  # ✅ CRITICAL: Link to specific video
                    word=vocab['word'],
                    translation=vocab['translation'],
                    pronunciation=vocab.get('pronunciation', ''),
                    part_of_speech=vocab.get('part_of_speech', 'word'),
                    example_sentence=vocab.get('example_sentence', ''),
                    example_translation=vocab.get('example_translation', ''),
                    language=language,
                    difficulty_level=vocab.get('difficulty_level', 'intermediate')
                )
                
                db.session.add(new_vocab)
                db.session.flush()  # Get vocab_id
                
                vocab_ids.append(new_vocab.vocab_id)
                
                logger.info(f"✅ Saved vocab {idx + 1}/{len(vocabularies)}: {vocab['word']} (ID: {new_vocab.vocab_id})")
                
            except Exception as e:
                logger.error(f"❌ Error saving vocab {idx + 1} ({vocab.get('word', 'unknown')}): {str(e)}")
                continue
        
        db.session.commit()
        
        logger.info(f"✅ Successfully saved {len(vocab_ids)}/{len(vocabularies)} vocabularies to database")
        
        if len(vocab_ids) == 0:
            return False, [], "Không lưu được từ vựng nào"
        
        return True, vocab_ids, f"Đã lưu {len(vocab_ids)} từ vựng"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Database error: {str(e)}", exc_info=True)
        return False, [], f"Lỗi lưu database: {str(e)}"


# ============= ALTERNATIVE METHOD =============

def extract_vocabulary_from_video_context(segments, video_language, max_words=15):
    """
    ✅ ALTERNATIVE: Trích xuất từ vựng dựa trên context của video
    
    Phương pháp này sử dụng CẢ text gốc VÀ translation để GPT-4 hiểu rõ hơn
    
    Args:
        segments: List of segments with text and translation
        video_language: Language code
        max_words: Number of words to extract
    
    Returns:
        tuple: (success, vocabularies, message)
    """
    try:
        # Lấy text và translation
        texts = [seg.get('text', '') for seg in segments[:50] if seg.get('text')]
        translations = [seg.get('translation', '') for seg in segments[:50] if seg.get('translation')]
        
        if not texts:
            return False, [], "Không có text"
        
        full_text = " ".join(texts)
        full_translation = " ".join(translations) if translations else ""
        
        logger.info(f"📚 Extracting {max_words} vocabularies from video context ({video_language})")
        
        # ✅ FIX: Tách phần có \n ra ngoài f-string
        translation_section = f"DỊCH TIẾNG VIỆT:\n{full_translation}" if full_translation else ""
        
        prompt = f"""Trích xuất {max_words} từ vựng QUAN TRỌNG từ video {video_language.upper()} này.

NGUYÊN VĂN ({video_language.upper()}):
{full_text}

{translation_section}

YÊU CẦU:
1. Chọn từ/cụm từ XUẤT HIỆN trong video
2. Từ phải bằng {video_language.upper()}
3. Ưu tiên từ hữu ích, quan trọng
4. Giữ response ngắn gọn

Trả về JSON (không markdown):
[
  {{
    "word": "từ gốc ({video_language})",
    "translation": "nghĩa tiếng Việt",
    "pronunciation": "phiên âm/romanization",
    "part_of_speech": "noun/verb/etc",
    "example_sentence": "câu ví dụ từ video",
    "example_translation": "dịch câu ví dụ",
    "difficulty_level": "basic/intermediate/advanced"
  }}
]"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a {video_language} vocabulary expert. Extract words from the provided video content. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown
        if "```" in content:
            content = content.replace("```json", "").replace("```", "").strip()
        
        # Parse
        result = json.loads(content)
        
        # Extract list
        if isinstance(result, dict):
            for key in ['vocabularies', 'words', 'vocabulary', 'items']:
                if key in result and isinstance(result[key], list):
                    result = result[key]
                    break
        
        # Validate and clean
        cleaned = []
        for v in result:
            if v.get('word') and v.get('translation') and '???' not in v['word']:
                cleaned.append({
                    'word': v['word'].strip(),
                    'translation': v['translation'].strip(),
                    'pronunciation': v.get('pronunciation', '').strip() or f"[{v['word']}]",
                    'part_of_speech': v.get('part_of_speech', 'word').strip(),
                    'example_sentence': v.get('example_sentence', '').strip(),
                    'example_translation': v.get('example_translation', '').strip(),
                    'difficulty_level': v.get('difficulty_level', 'intermediate').strip()
                })
        
        logger.info(f"✅ Extracted {len(cleaned)} vocabularies from video context")
        
        return True, cleaned, "Trích xuất thành công"
        
    except Exception as e:
        logger.error(f"❌ Error in video context extraction: {str(e)}", exc_info=True)
        return False, [], str(e)