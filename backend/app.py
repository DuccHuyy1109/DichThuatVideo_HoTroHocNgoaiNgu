"""
Main Application File
Hệ thống trích xuất phụ đề và dịch thuật video tự động
"""
import sys
import io
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config, Config
from database.db_config import db, init_db
from middleware.error_handler import register_error_handlers
from utils.response_handler import success_response, error_response
from api.video_stream import video_stream_bp


# Import các routes
from api.auth import auth_bp
from api.videos import videos_bp
from api.subtitles import subtitles_bp
from api.quiz import quiz_bp
from api.vocabulary import vocabulary_bp
from api.users import users_bp
from api.process import process_bp

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
def create_app(config_name='development'):
    """
    Factory function để tạo Flask application
    
    Args:
        config_name: Tên cấu hình (development, production, testing)
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Disable strict slashes to avoid 308 redirects
    app.url_map.strict_slashes = False
    
    # Load configuration
    app.config.from_object(config[config_name])

        # ========== ADD THESE LINES ==========
    # Force UTF-8
    app.config['JSON_AS_ASCII'] = False
    
    @app.after_request
    def after_request(response):
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    # ====================================
    
    # Khởi tạo các thư mục cần thiết
    Config.init_folders()
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    jwt = JWTManager(app)
    
    # Initialize database
    db.init_app(app)
    with app.app_context():
        init_db()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints (API routes)
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(videos_bp, url_prefix='/api/v1/videos')
    app.register_blueprint(subtitles_bp, url_prefix='/api/v1/subtitles')
    app.register_blueprint(quiz_bp, url_prefix='/api/v1/quiz')
    app.register_blueprint(vocabulary_bp, url_prefix='/api/v1/vocabulary')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(process_bp, url_prefix='/api/v1/process')
    app.register_blueprint(video_stream_bp, url_prefix='/api/v1/videos')

    
    # Health check route
    @app.route('/')
    def index():
        return jsonify(success_response(
            message='API Hệ thống trích xuất phụ đề và dịch thuật video đang hoạt động',
            data={
                'version': '1.0.0',
                'status': 'running',
                'endpoints': {
                    'auth': '/api/v1/auth',
                    'videos': '/api/v1/videos',
                    'subtitles': '/api/v1/subtitles',
                    'quiz': '/api/v1/quiz',
                    'vocabulary': '/api/v1/vocabulary',
                    'users': '/api/v1/users',
                    'process': '/api/v1/process'
                }
            }
        ))
    
    @app.route('/api/v1/health')
    def health_check():
        return jsonify(success_response(
            message='Hệ thống hoạt động bình thường',
            data={'status': 'healthy'}
        ))
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        app.logger.warning('Token expired')
        return jsonify(error_response(
            message='Token đã hết hạn',
            status_code=401
        )), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        app.logger.warning(f'Invalid token: {error}')
        return jsonify(error_response(
            message='Token không hợp lệ',
            status_code=401
        )), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        app.logger.warning(f'Missing token: {error}')
        return jsonify(error_response(
            message='Thiếu token xác thực',
            status_code=401
        )), 401
    
    app.logger.info('Application khởi tạo thành công')
    
    return app


def setup_logging(app):
    """
    Setup logging cho application
    
    Args:
        app: Flask app instance
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    log_file = app.config['LOG_FILE']
    
    # Tạo thư mục logs nếu chưa tồn tại
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Set Flask logger
    app.logger.setLevel(log_level)


if __name__ == '__main__':
    # Lấy config name từ biến môi trường
    config_name = os.getenv('FLASK_ENV', 'development')
    
    # Tạo app
    app = create_app(config_name)
    
    # Chạy server
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )