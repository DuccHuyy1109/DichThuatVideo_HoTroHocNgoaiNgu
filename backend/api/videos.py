"""
Videos API Routes
API cho quản lý video
"""
import logging
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from database.models import Video
from database.db_config import db
from middleware.auth_middleware import get_current_user
from utils.response_handler import success_response, error_response, paginated_response
from utils.validators import validate_video_file
from utils.file_handler import save_uploaded_file, delete_file
from utils.constants import VIDEO_STATUS_PENDING, SUCCESS_VIDEO_UPLOAD, SUCCESS_VIDEO_DELETE
from config import Config

logger = logging.getLogger(__name__)

# Tạo Blueprint
videos_bp = Blueprint('videos', __name__)


@videos_bp.route('/', methods=['GET'])
@jwt_required()
def get_videos():
    """
    API lấy danh sách video của user
    
    Query params:
    - page: Trang (default: 1)
    - per_page: Số video mỗi trang (default: 10)
    - status: Lọc theo status (optional)
    """
    try:
        user = get_current_user()
        
        # Lấy params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)
        
        # Query
        query = Video.query.filter_by(user_id=user.user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by upload_date desc
        query = query.order_by(Video.upload_date.desc())
        
        # Pagination
        total_items = query.count()
        videos = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict
        videos_data = [video.to_dict() for video in videos]
        
        return jsonify(paginated_response(
            items=videos_data,
            page=page,
            per_page=per_page,
            total_items=total_items,
            message='Lấy danh sách video thành công'
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_videos: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy danh sách video',
            status_code=500,
            error=str(e)
        )), 500


@videos_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """
    API lấy chi tiết video
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
        
        return jsonify(success_response(
            message='Lấy thông tin video thành công',
            data={'video': video.to_dict()}
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_video: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy thông tin video',
            status_code=500,
            error=str(e)
        )), 500


@videos_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_video():
    """
    API upload video
    
    Form data:
    - file: Video file
    - title: Tiêu đề video (optional)
    """
    try:
        user = get_current_user()
        
        # Kiểm tra file
        if 'file' not in request.files:
            return jsonify(error_response(
                message='Không có file được upload',
                status_code=400
            )), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify(error_response(
                message='Không có file được chọn',
                status_code=400
            )), 400
        
        # Validate file
        is_valid, message = validate_video_file(
            file.filename,
            Config.ALLOWED_VIDEO_EXTENSIONS
        )
        
        if not is_valid:
            return jsonify(error_response(
                message=message,
                status_code=400
            )), 400
        
        # Lấy title
        title = request.form.get('title', file.filename)
        
        # Lưu file
        success, file_path, save_message = save_uploaded_file(
            file=file,
            upload_folder=Config.UPLOAD_FOLDER,
            subfolder='videos'
        )
        
        if not success:
            return jsonify(error_response(
                message=save_message,
                status_code=500
            )), 500
        
        # Tạo video record
        video = Video(
            user_id=user.user_id,
            title=title,
            original_filename=secure_filename(file.filename),
            file_path=file_path,
            status=VIDEO_STATUS_PENDING
        )
        
        db.session.add(video)
        db.session.commit()
        
        logger.info(f"Video uploaded: {video.video_id}")
        
        # AUTO-START PROCESSING IN BACKGROUND
        try:
            import threading
            from modules.video_processor.process_video import process_video_background
            
            thread = threading.Thread(
                target=process_video_background,
                args=(video.video_id,)
            )
            thread.daemon = True
            thread.start()
            
            logger.info(f"Auto-started processing for video {video.video_id}")
        except Exception as e:
            logger.error(f"Error starting auto-process: {str(e)}")
        
        return jsonify(success_response(
            message=SUCCESS_VIDEO_UPLOAD,
            data={'video': video.to_dict()}
        )), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi API upload_video: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi upload video',
            status_code=500,
            error=str(e)
        )), 500


@videos_bp.route('/<int:video_id>', methods=['DELETE'])
@jwt_required()
def delete_video(video_id):
    """
    API xóa video
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
        
        # Xóa file
        if video.file_path and os.path.exists(video.file_path):
            delete_file(video.file_path)
        
        # Xóa record
        db.session.delete(video)
        db.session.commit()
        
        logger.info(f"Video deleted: {video_id}")
        
        return jsonify(success_response(
            message=SUCCESS_VIDEO_DELETE
        )), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi API delete_video: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi xóa video',
            status_code=500,
            error=str(e)
        )), 500


@videos_bp.route('/<int:video_id>/status', methods=['GET'])
@jwt_required()
def get_video_status(video_id):
    """
    API lấy trạng thái xử lý video
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
        
        return jsonify(success_response(
            message='Lấy trạng thái thành công',
            data={
                'video_id': video.video_id,
                'status': video.status,
                'title': video.title
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_video_status: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy trạng thái',
            status_code=500,
            error=str(e)
        )), 500


@videos_bp.route('/<int:video_id>', methods=['PUT'])
@jwt_required()
def update_video(video_id):
    """
    API cập nhật thông tin video
    
    Request body:
    {
        "title": "string"
    }
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Tìm video
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # Cập nhật title
        if 'title' in data:
            video.title = data['title']
        
        db.session.commit()
        
        return jsonify(success_response(
            message='Cập nhật video thành công',
            data={'video': video.to_dict()}
        )), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi API update_video: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi cập nhật video',
            status_code=500,
            error=str(e)
        )), 500