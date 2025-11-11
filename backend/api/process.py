"""
Video Processing API
API để xử lý video (speech-to-text, translation, subtitle, quiz, vocabulary)
"""
import logging
import threading
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from database.models import Video
from middleware.auth_middleware import get_current_user
from modules.video_processor.process_video import process_video_background
from utils.response_handler import success_response, error_response

logger = logging.getLogger(__name__)

# Tạo Blueprint
process_bp = Blueprint('process', __name__)


@process_bp.route('/video/<int:video_id>', methods=['POST'])
@jwt_required()
def process_video(video_id):
    """
    API xử lý video
    Bắt đầu quá trình xử lý video trong background
    
    Path params:
        video_id: ID của video
    
    Returns:
        202: Đã bắt đầu xử lý
        404: Video không tồn tại
        403: Không có quyền
    """
    try:
        user = get_current_user()
        
        # Kiểm tra video tồn tại và thuộc về user
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # Kiểm tra status
        if video.status == 'processing':
            return jsonify(error_response(
                message='Video đang được xử lý',
                status_code=400
            )), 400
        
        if video.status == 'completed':
            return jsonify(success_response(
                message='Video đã được xử lý trước đó',
                data={'video': video.to_dict()}
            )), 200
        
        # Get app instance để truyền vào background thread
        app = current_app._get_current_object()
        
        # Start processing in background thread
        thread = threading.Thread(
            target=process_video_background,
            args=(video_id, app)  # Truyền app instance vào
        )
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started background processing for video {video_id}")
        
        return jsonify(success_response(
            message='Đã bắt đầu xử lý video. Quá trình có thể mất vài phút.',
            data={
                'video_id': video_id,
                'status': 'processing'
            }
        )), 202
        
    except Exception as e:
        logger.error(f"Lỗi API process_video: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi xử lý video',
            status_code=500,
            error=str(e)
        )), 500


@process_bp.route('/status/<int:video_id>', methods=['GET'])
@jwt_required()
def get_processing_status(video_id):
    """
    API lấy trạng thái xử lý video
    
    Path params:
        video_id: ID của video
    
    Returns:
        200: Trạng thái video
        404: Video không tồn tại
    """
    try:
        user = get_current_user()
        
        # Kiểm tra video
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # Get subtitle count
        from database.models import Subtitle, Quiz
        subtitle_count = Subtitle.query.filter_by(video_id=video_id).count()
        quiz_count = Quiz.query.filter_by(video_id=video_id).count()
        
        return jsonify(success_response(
            message='Lấy trạng thái thành công',
            data={
                'video': video.to_dict(),
                'subtitle_count': subtitle_count,
                'quiz_count': quiz_count,
                'is_ready': video.status == 'completed'
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_processing_status: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy trạng thái',
            status_code=500,
            error=str(e)
        )), 500