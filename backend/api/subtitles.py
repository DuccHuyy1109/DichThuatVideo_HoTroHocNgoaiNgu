"""
Subtitles API Routes
API cho quản lý phụ đề
"""
import logging
import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.models import Subtitle, Video
from database.db_config import db
from middleware.auth_middleware import get_current_user
from utils.response_handler import success_response, error_response

logger = logging.getLogger(__name__)

# Tạo Blueprint
subtitles_bp = Blueprint('subtitles', __name__)


@subtitles_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_subtitles(video_id):
    """
    API lấy phụ đề của video
    
    Query params:
    - language: Mã ngôn ngữ (optional)
    """
    try:
        user = get_current_user()
        
        # Kiểm tra video thuộc về user
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # Lấy language filter
        language = request.args.get('language', None)
        
        # Query subtitles
        query = Subtitle.query.filter_by(video_id=video_id)
        
        if language:
            query = query.filter_by(language=language)
        
        subtitles = query.all()
        
        # Convert to dict
        subtitles_data = [subtitle.to_dict() for subtitle in subtitles]
        
        return jsonify(success_response(
            message='Lấy phụ đề thành công',
            data={'subtitles': subtitles_data}
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_subtitles: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy phụ đề',
            status_code=500,
            error=str(e)
        )), 500


@subtitles_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_subtitle():
    """
    API tạo phụ đề cho video
    
    Request body:
    {
        "video_id": int,
        "source_language": "string" (optional, default: "auto"),
        "target_language": "string" (optional, default: "vi")
    }
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'video_id' not in data:
            return jsonify(error_response(
                message='Thiếu video_id',
                status_code=400
            )), 400
        
        video_id = data['video_id']
        source_language = data.get('source_language', 'auto')
        target_language = data.get('target_language', 'vi')
        
        # Kiểm tra video
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # TODO: Implement subtitle generation logic
        # Sẽ được implement ở modules/subtitle/subtitle_generator.py
        
        return jsonify(success_response(
            message='Đang xử lý tạo phụ đề. Vui lòng kiểm tra lại sau.',
            data={
                'video_id': video_id,
                'status': 'processing'
            }
        )), 202
        
    except Exception as e:
        logger.error(f"Lỗi API generate_subtitle: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi tạo phụ đề',
            status_code=500,
            error=str(e)
        )), 500


@subtitles_bp.route('/download/<int:subtitle_id>', methods=['GET'])
@jwt_required()
def download_subtitle(subtitle_id):
    """
    API tải xuống file phụ đề
    
    Query params:
    - format: srt hoặc vtt (optional, default: srt)
    """
    try:
        user = get_current_user()
        
        # Tìm subtitle
        subtitle = Subtitle.query.get(subtitle_id)
        
        if not subtitle:
            return jsonify(error_response(
                message='Không tìm thấy phụ đề',
                status_code=404
            )), 404
        
        # Kiểm tra quyền truy cập
        video = Video.query.filter_by(video_id=subtitle.video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không có quyền truy cập',
                status_code=403
            )), 403
        
        # Lấy format
        download_format = request.args.get('format', 'srt')
        
        # Kiểm tra file tồn tại
        if not subtitle.file_path or not os.path.exists(subtitle.file_path):
            return jsonify(error_response(
                message='File phụ đề không tồn tại',
                status_code=404
            )), 404
        
        # Download file
        return send_file(
            subtitle.file_path,
            as_attachment=True,
            download_name=f"{video.title}_{subtitle.language}.{download_format}"
        )
        
    except Exception as e:
        logger.error(f"Lỗi API download_subtitle: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi tải xuống phụ đề',
            status_code=500,
            error=str(e)
        )), 500


@subtitles_bp.route('/<int:subtitle_id>', methods=['DELETE'])
@jwt_required()
def delete_subtitle(subtitle_id):
    """
    API xóa phụ đề
    """
    try:
        user = get_current_user()
        
        # Tìm subtitle
        subtitle = Subtitle.query.get(subtitle_id)
        
        if not subtitle:
            return jsonify(error_response(
                message='Không tìm thấy phụ đề',
                status_code=404
            )), 404
        
        # Kiểm tra quyền
        video = Video.query.filter_by(video_id=subtitle.video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không có quyền truy cập',
                status_code=403
            )), 403
        
        # Xóa file
        if subtitle.file_path and os.path.exists(subtitle.file_path):
            os.remove(subtitle.file_path)
        
        # Xóa record
        db.session.delete(subtitle)
        db.session.commit()
        
        return jsonify(success_response(
            message='Xóa phụ đề thành công'
        )), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi API delete_subtitle: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi xóa phụ đề',
            status_code=500,
            error=str(e)
        )), 500