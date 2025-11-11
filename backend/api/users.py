"""
Users API Routes
API cho quản lý người dùng
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.models import LearningProgress, Video
from database.db_config import db
from middleware.auth_middleware import get_current_user
from modules.auth import change_password
from utils.response_handler import success_response, error_response


logger = logging.getLogger(__name__)

# Tạo Blueprint
users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    API lấy thông tin profile
    """
    try:
        user = get_current_user()
        
        if not user:
            return jsonify(error_response(
                message='Không tìm thấy người dùng',
                status_code=404
            )), 404
        
        return jsonify(success_response(
            message='Lấy thông tin profile thành công',
            data={'user': user.to_dict()}
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_profile: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy thông tin profile',
            status_code=500,
            error=str(e)
        )), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    API cập nhật profile
    
    Request body:
    {
        "full_name": "string" (optional),
        "email": "string" (optional)
    }
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify(error_response(
                message='Dữ liệu không hợp lệ',
                status_code=400
            )), 400
        
        # Cập nhật full_name
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        # Cập nhật email
        if 'email' in data:
            from utils.validators import validate_email
            is_valid, message = validate_email(data['email'])
            
            if not is_valid:
                return jsonify(error_response(
                    message=message,
                    status_code=400
                )), 400
            
            # Kiểm tra email đã tồn tại
            from database.models import User
            existing_email = User.query.filter(
                User.email == data['email'],
                User.user_id != user.user_id
            ).first()
            
            if existing_email:
                return jsonify(error_response(
                    message='Email đã được sử dụng',
                    status_code=400
                )), 400
            
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify(success_response(
            message='Cập nhật profile thành công',
            data={'user': user.to_dict()}
        )), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi API update_profile: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi cập nhật profile',
            status_code=500,
            error=str(e)
        )), 500


@users_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_user_password():
    """
    API đổi mật khẩu
    
    Request body:
    {
        "old_password": "string",
        "new_password": "string"
    }
    """
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data or 'old_password' not in data or 'new_password' not in data:
            return jsonify(error_response(
                message='Thiếu thông tin bắt buộc',
                status_code=400
            )), 400
        
        old_password = data['old_password']
        new_password = data['new_password']
        
        # Đổi mật khẩu
        success, message = change_password(user, old_password, new_password)
        
        if not success:
            return jsonify(error_response(
                message=message,
                status_code=400
            )), 400
        
        return jsonify(success_response(
            message=message
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API change_password: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi đổi mật khẩu',
            status_code=500,
            error=str(e)
        )), 500


@users_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_learning_progress():
    """
    API lấy tiến trình học tập
    
    Query params:
    - video_id: Lọc theo video (optional)
    """
    try:
        user = get_current_user()
        
        # Lấy video_id filter
        video_id = request.args.get('video_id', None, type=int)
        
        # Query progress
        query = LearningProgress.query.filter_by(user_id=user.user_id)
        
        if video_id:
            query = query.filter_by(video_id=video_id)
        
        progress_list = query.all()
        
        # Convert to dict và join với Video
        progress_data = []
        for progress in progress_list:
            video = Video.query.get(progress.video_id)
            if video:
                progress_dict = progress.to_dict()
                progress_dict['video_title'] = video.title
                progress_data.append(progress_dict)
        
        return jsonify(success_response(
            message='Lấy tiến trình học tập thành công',
            data={'progress': progress_data}
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_learning_progress: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy tiến trình học tập',
            status_code=500,
            error=str(e)
        )), 500


@users_bp.route('/progress', methods=['POST'])
@jwt_required()
def update_learning_progress():
    """
    API cập nhật tiến trình học tập
    
    Request body:
    {
        "video_id": int,
        "watch_duration": float,
        "completion_percentage": float
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
        watch_duration = data.get('watch_duration', 0)
        completion_percentage = data.get('completion_percentage', 0)
        
        # Kiểm tra video
        video = Video.query.filter_by(video_id=video_id, user_id=user.user_id).first()
        
        if not video:
            return jsonify(error_response(
                message='Không tìm thấy video',
                status_code=404
            )), 404
        
        # Tìm hoặc tạo progress
        progress = LearningProgress.query.filter_by(
            user_id=user.user_id,
            video_id=video_id
        ).first()
        
        from datetime import datetime
        
        if progress:
            # Cập nhật
            progress.watch_duration = watch_duration
            progress.completion_percentage = completion_percentage
            progress.last_watched = datetime.utcnow()
            progress.watch_count += 1
        else:
            # Tạo mới
            progress = LearningProgress(
                user_id=user.user_id,
                video_id=video_id,
                watch_duration=watch_duration,
                completion_percentage=completion_percentage,
                last_watched=datetime.utcnow(),
                watch_count=1
            )
            db.session.add(progress)
        
        db.session.commit()
        
        return jsonify(success_response(
            message='Cập nhật tiến trình thành công',
            data={'progress': progress.to_dict()}
        )), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi API update_learning_progress: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi cập nhật tiến trình',
            status_code=500,
            error=str(e)
        )), 500