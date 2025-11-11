"""
Video Streaming API - Serve video files
Thêm vào videos.py hoặc tạo file riêng
"""
import logging
import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.models import Video
from middleware.auth_middleware import get_current_user
from utils.response_handler import error_response

logger = logging.getLogger(__name__)

# Blueprint
video_stream_bp = Blueprint('video_stream', __name__)


@video_stream_bp.route('/stream/<int:video_id>', methods=['GET'])
@jwt_required()
def stream_video(video_id):
    """
    Stream video file
    Path: /api/v1/videos/stream/<video_id>
    """
    try:
        user = get_current_user()
        
        # Tìm video
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # Kiểm tra file tồn tại
        if not os.path.exists(video.file_path):
            return jsonify(error_response(
                message='File video không tồn tại',
                status_code=404
            )), 404
        
        # Stream video
        return send_file(
            video.file_path,
            mimetype='video/mp4',
            as_attachment=False,
            download_name=video.original_filename
        )
        
    except Exception as e:
        logger.error(f"Lỗi stream video: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi stream video',
            status_code=500,
            error=str(e)
        )), 500


@video_stream_bp.route('/download/<int:video_id>', methods=['GET'])
@jwt_required()
def download_video(video_id):
    """
    Download video file
    """
    try:
        user = get_current_user()
        
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video or not os.path.exists(video.file_path):
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        return send_file(
            video.file_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=video.original_filename
        )
        
    except Exception as e:
        logger.error(f"Lỗi download video: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi download video',
            status_code=500,
            error=str(e)
        )), 500