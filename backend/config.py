"""
Configuration file cho ứng dụng
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database Configuration
    DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    DB_SERVER = os.getenv('DB_SERVER', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'VideoSubtitleDB')
    DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = os.getenv('DB_PORT', '1433')
    
    # Tạo connection string cho SQL Server
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"
        f"?driver={DB_DRIVER.replace(' ', '+')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    
    # Whisper Configuration
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'medium')
    WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cpu')
    WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'int8')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 524288000))  # 500MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_VIDEO_EXTENSIONS = set(
        os.getenv('ALLOWED_VIDEO_EXTENSIONS', 'mp4,avi,mov,mkv,flv,wmv').split(',')
    )
    MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', 7200))  # 2 giờ
    
    # Storage Paths
    STORAGE_FOLDER = os.getenv('STORAGE_FOLDER', 'storage')
    SUBTITLES_FOLDER = os.getenv('SUBTITLES_FOLDER', 'storage/subtitles')
    AUDIO_FOLDER = os.getenv('AUDIO_FOLDER', 'storage/processed_audio')
    DOWNLOADS_FOLDER = os.getenv('DOWNLOADS_FOLDER', 'storage/downloads')
    
    # Tạo các thư mục nếu chưa tồn tại
    @staticmethod
    def init_folders():
        folders = [
            Config.UPLOAD_FOLDER,
            os.path.join(Config.UPLOAD_FOLDER, 'videos'),
            os.path.join(Config.UPLOAD_FOLDER, 'audio'),
            os.path.join(Config.UPLOAD_FOLDER, 'temp'),
            Config.STORAGE_FOLDER,
            Config.SUBTITLES_FOLDER,
            Config.AUDIO_FOLDER,
            Config.DOWNLOADS_FOLDER,
            'logs'
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000').split(',')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    # Language Configuration
    DEFAULT_SOURCE_LANGUAGE = os.getenv('DEFAULT_SOURCE_LANGUAGE', 'auto')
    DEFAULT_TARGET_LANGUAGE = os.getenv('DEFAULT_TARGET_LANGUAGE', 'vi')
    SUPPORTED_LANGUAGES = os.getenv(
        'SUPPORTED_LANGUAGES', 
        'en,vi,ja,ko,zh,fr,de,es'
    ).split(',')
    
    # Vocabulary Settings
    MIN_WORD_LENGTH = 3
    MAX_VOCABULARY_PER_VIDEO = 20
    
    # Quiz Settings
    QUIZ_QUESTIONS_PER_VIDEO = 10
    QUIZ_OPTIONS_COUNT = 4

    JSON_AS_ASCII = False  # CRITICAL!
    JSONIFY_MIMETYPE = 'application/json; charset=utf-8'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dictionary để chọn config
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}