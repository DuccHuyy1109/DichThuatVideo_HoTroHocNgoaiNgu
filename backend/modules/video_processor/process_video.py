"""
Main Video Processing Module - COMPLETE FIXED VERSION
Xử lý hoàn chỉnh video: Speech-to-Text, Translation, Subtitle, Quiz, Vocabulary

VỊ TRÍ FILE: backend/modules/video_processor/process_video.py
"""
import logging
import os
from datetime import datetime
from flask import current_app
from database.models import Video, Subtitle
from database.db_config import db
from modules.video_processor import extract_audio_from_video, get_video_info
from modules.speech_to_text import transcribe_audio_whisper
from modules.translation import translate_segments_gpt4
from modules.subtitle import generate_subtitle_file, create_bilingual_subtitle
from modules.quiz import generate_quiz_from_transcript, save_quizzes_to_database
from modules.vocabulary import extract_vocabulary_from_transcript, save_vocabulary_to_database
from config import Config

logger = logging.getLogger(__name__)


def process_video_complete(video_id, app=None):
    """
    Xử lý hoàn chỉnh video
    
    Args:
        video_id: ID của video
        app: Flask app instance (bắt buộc cho background processing)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Nếu không có app, lấy từ current_app
    if app is None:
        app = current_app._get_current_object()
    
    # Chạy trong app context
    with app.app_context():
        try:
            # Get video từ database
            video = Video.query.get(video_id)
            
            if not video:
                return False, "Video không tồn tại"
            
            logger.info(f"🎬 Bắt đầu xử lý video ID: {video_id}")
            
            # Update status
            video.status = 'processing'
            db.session.commit()
            
            # Step 1: Validate và lấy thông tin video
            logger.info("📹 Step 1: Lấy thông tin video...")
            video_info = get_video_info(video.file_path)
            
            if not video_info:
                video.status = 'failed'
                db.session.commit()
                return False, "Không thể đọc thông tin video"
            
            video.duration = video_info['duration']
            db.session.commit()
            
            # Step 2: Trích xuất audio
            logger.info("🎵 Step 2: Trích xuất audio...")
            success, audio_path, msg = extract_audio_from_video(video.file_path)
            
            if not success:
                video.status = 'failed'
                db.session.commit()
                return False, f"Lỗi trích xuất audio: {msg}"
            
            # Step 3: Speech to Text
            logger.info("🎤 Step 3: Speech to Text với Whisper...")
            success, transcription_result, msg = transcribe_audio_whisper(
                audio_path,
                language=None  # Auto detect
            )
            
            if not success:
                video.status = 'failed'
                db.session.commit()
                return False, f"Lỗi Speech-to-Text: {msg}"
            
            segments = transcription_result['segments']
            detected_language = transcription_result['language']
            
            # Update detected language
            video.language_detected = detected_language
            db.session.commit()
            
            logger.info(f"✅ Detected language: {detected_language}, Segments: {len(segments)}")
            
            # Step 4: Translation
            logger.info("🌐 Step 4: Dịch segments sang tiếng Việt...")
            success, translated_segments, msg = translate_segments_gpt4(
                segments,
                source_language=detected_language,
                target_language='vi'
            )
            
            if not success:
                logger.warning(f"⚠️ Lỗi dịch: {msg}. Tiếp tục với segments gốc...")
                translated_segments = segments
            
            # Step 5: Tạo phụ đề
            logger.info("📝 Step 5: Tạo phụ đề...")
            
            # Tạo phụ đề song ngữ SRT
            subtitle_path = os.path.join(
                Config.SUBTITLES_FOLDER,
                f"video_{video_id}_bilingual.srt"
            )
            
            success, file_path, msg = create_bilingual_subtitle(
                translated_segments,
                subtitle_path,
                subtitle_format='srt'
            )
            
            if success:
                # Lưu subtitle vào database
                import json
                subtitle = Subtitle(
                    video_id=video_id,
                    language='vi',
                    content=json.dumps(translated_segments),  # JSON string
                    file_path=file_path,
                    subtitle_format='srt'
                )
                db.session.add(subtitle)
                db.session.commit()
                
                logger.info(f"✅ Phụ đề đã được lưu: {file_path}")
            
            # ✅ Step 6: Trích xuất từ vựng - FIXED WITH VIDEO_ID
            logger.info("📚 Step 6: Trích xuất từ vựng...")
            
            try:
                success, vocabularies, msg = extract_vocabulary_from_transcript(
                    segments=translated_segments,
                    video_language=detected_language,  # ✅ Pass detected language
                    max_words=Config.MAX_VOCABULARY_PER_VIDEO
                )
                
                if success and vocabularies and len(vocabularies) > 0:
                    # ✅ FIXED: Pass video_id để link với video
                    success, vocab_ids, msg = save_vocabulary_to_database(
                        vocabularies=vocabularies,
                        language=detected_language,
                        video_id=video_id,  # ✅ NEW: Link to specific video
                        db=db
                    )
                    
                    if success:
                        logger.info(f"✅ Đã lưu {len(vocab_ids)} từ vựng cho video {video_id}")
                    else:
                        logger.warning(f"⚠️ Lỗi lưu từ vựng: {msg}")
                else:
                    logger.warning(f"⚠️ Không trích xuất được từ vựng: {msg}")
                    
            except Exception as e:
                logger.error(f"❌ Lỗi trích xuất từ vựng: {str(e)}", exc_info=True)
                # Continue processing even if vocabulary extraction fails
            
            # Step 7: Tạo quiz
            logger.info("❓ Step 7: Tạo quiz...")
            
            try:
                success, quizzes, msg = generate_quiz_from_transcript(
                    translated_segments,
                    num_questions=Config.QUIZ_QUESTIONS_PER_VIDEO
                )
                
                if success and quizzes and len(quizzes) > 0:
                    success, msg = save_quizzes_to_database(quizzes, video_id, db)
                    
                    if success:
                        logger.info(f"✅ Đã tạo {len(quizzes)} câu quiz")
                    else:
                        logger.warning(f"⚠️ Lỗi lưu quiz: {msg}")
                else:
                    logger.warning(f"⚠️ Không tạo được quiz: {msg}")
                    
            except Exception as e:
                logger.error(f"❌ Lỗi tạo quiz: {str(e)}", exc_info=True)
                # Continue processing even if quiz generation fails
            
            # Step 8: Update video status
            video.status = 'completed'
            video.processed_date = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"✅ Xử lý video {video_id} hoàn tất!")
            
            # Cleanup audio file
            try:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    logger.info(f"🗑️ Đã xóa file audio tạm: {audio_path}")
            except Exception as e:
                logger.warning(f"⚠️ Không xóa được audio file: {str(e)}")
            
            return True, "Xử lý video thành công"
            
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý video: {str(e)}", exc_info=True)
            
            # Update status to failed
            try:
                video = Video.query.get(video_id)
                if video:
                    video.status = 'failed'
                    db.session.commit()
            except:
                pass
            
            return False, f"Lỗi xử lý video: {str(e)}"


def process_video_background(video_id, app):
    """
    Xử lý video trong background (để dùng với threading)
    
    Args:
        video_id: ID của video
        app: Flask app instance (BẮT BUỘC)
    """
    try:
        success, message = process_video_complete(video_id, app)
        
        if success:
            logger.info(f"✅ Background processing completed for video {video_id}")
        else:
            logger.error(f"❌ Background processing failed for video {video_id}: {message}")
            
    except Exception as e:
        logger.error(f"❌ Background processing error: {str(e)}", exc_info=True)