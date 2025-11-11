"""
Authentication API Routes
API cho đăng ký, đăng nhập, đăng xuất
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from modules.auth import register_user, login_user
from middleware.auth_middleware import get_current_user
from utils.response_handler import success_response, error_response
from utils.constants import SUCCESS_REGISTER, SUCCESS_LOGIN, SUCCESS_LOGOUT

logger = logging.getLogger(__name__)

# Tạo Blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """API đăng ký người dùng mới"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(error_response(
                message='Dữ liệu không hợp lệ',
                status_code=400
            )), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if not username or not email or not password:
            return jsonify(error_response(
                message='Thiếu thông tin bắt buộc',
                status_code=400
            )), 400
        
        success, user, message = register_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        if not success:
            return jsonify(error_response(
                message=message,
                status_code=400
            )), 400
        
        # QUAN TRỌNG: Convert user_id sang STRING
        access_token = create_access_token(identity=str(user.user_id))
        
        return jsonify(success_response(
            message=SUCCESS_REGISTER,
            data={
                'user': user.to_dict(),
                'access_token': access_token
            }
        )), 201
        
    except Exception as e:
        logger.error(f"Lỗi API register: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi đăng ký',
            status_code=500,
            error=str(e)
        )), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """API đăng nhập"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(error_response(
                message='Dữ liệu không hợp lệ',
                status_code=400
            )), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify(error_response(
                message='Thiếu thông tin đăng nhập',
                status_code=400
            )), 400
        
        success, user, message = login_user(
            username=username,
            password=password
        )
        
        if not success:
            return jsonify(error_response(
                message=message,
                status_code=401
            )), 401
        
        # QUAN TRỌNG: Convert user_id sang STRING
        access_token = create_access_token(identity=str(user.user_id))
        
        logger.info(f"✅ Token created for user_id: {user.user_id} (as string)")
        
        return jsonify(success_response(
            message=SUCCESS_LOGIN,
            data={
                'user': user.to_dict(),
                'access_token': access_token
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API login: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi đăng nhập',
            status_code=500,
            error=str(e)
        )), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """API đăng xuất"""
    try:
        return jsonify(success_response(
            message=SUCCESS_LOGOUT
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API logout: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi đăng xuất',
            status_code=500,
            error=str(e)
        )), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """API xác thực token"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify(error_response(
                message='Token không hợp lệ',
                status_code=401
            )), 401
        
        logger.info(f"✅ Token verified for user: {user.username}")
        
        return jsonify(success_response(
            message='Token hợp lệ',
            data={'user': user.to_dict()}
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API verify: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi xác thực token',
            status_code=500,
            error=str(e)
        )), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """API lấy thông tin profile của user hiện tại"""
    try:
        user = get_current_user()
        
        if not user:
            return jsonify(error_response(
                message='Không tìm thấy người dùng',
                status_code=404
            )), 404
        
        return jsonify(success_response(
            message='Lấy thông tin thành công',
            data={'user': user.to_dict()}
        )), 200
        
    except Exception as e:
        logger.error(f"Lỗi API get_my_profile: {str(e)}")
        return jsonify(error_response(
            message='Lỗi khi lấy thông tin',
            status_code=500,
            error=str(e)
        )), 500