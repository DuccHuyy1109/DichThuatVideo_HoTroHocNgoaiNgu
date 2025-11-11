"""
Error Handler Middleware
Xử lý các lỗi trong ứng dụng
"""
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
from utils.response_handler import error_response

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Đăng ký các error handlers cho Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Xử lý lỗi Bad Request"""
        logger.warning(f"Bad Request: {str(error)}")
        return jsonify(error_response(
            message='Yêu cầu không hợp lệ',
            status_code=400,
            error=str(error)
        )), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Xử lý lỗi Unauthorized"""
        logger.warning(f"Unauthorized: {str(error)}")
        return jsonify(error_response(
            message='Không có quyền truy cập',
            status_code=401,
            error=str(error)
        )), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Xử lý lỗi Forbidden"""
        logger.warning(f"Forbidden: {str(error)}")
        return jsonify(error_response(
            message='Truy cập bị từ chối',
            status_code=403,
            error=str(error)
        )), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Xử lý lỗi Not Found"""
        logger.warning(f"Not Found: {str(error)}")
        return jsonify(error_response(
            message='Không tìm thấy tài nguyên',
            status_code=404,
            error=str(error)
        )), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Xử lý lỗi Method Not Allowed"""
        logger.warning(f"Method Not Allowed: {str(error)}")
        return jsonify(error_response(
            message='Phương thức không được phép',
            status_code=405,
            error=str(error)
        )), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Xử lý lỗi file quá lớn"""
        logger.warning(f"Request Entity Too Large: {str(error)}")
        return jsonify(error_response(
            message='File tải lên quá lớn. Vui lòng chọn file nhỏ hơn 500MB',
            status_code=413,
            error=str(error)
        )), 413
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Xử lý lỗi Internal Server Error"""
        logger.error(f"Internal Server Error: {str(error)}", exc_info=True)
        return jsonify(error_response(
            message='Lỗi máy chủ nội bộ',
            status_code=500,
            error=str(error)
        )), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Xử lý tất cả HTTP exceptions"""
        logger.warning(f"HTTP Exception: {error.code} - {str(error)}")
        return jsonify(error_response(
            message=error.description,
            status_code=error.code,
            error=str(error)
        )), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Xử lý tất cả các exception chung"""
        logger.error(f"Unhandled Exception: {str(error)}", exc_info=True)
        return jsonify(error_response(
            message='Đã xảy ra lỗi không mong muốn',
            status_code=500,
            error=str(error)
        )), 500
    
    logger.info("Error handlers đã được đăng ký thành công")