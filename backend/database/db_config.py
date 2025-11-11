"""
Database configuration và connection setup
"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Khởi tạo SQLAlchemy instance
db = SQLAlchemy()

logger = logging.getLogger(__name__)


def init_db():
    """
    Khởi tạo database và tạo các bảng
    """
    try:
        # Import models để SQLAlchemy nhận biết
        from .models import (
            User, Video, Subtitle, Vocabulary, 
            UserVocabulary, Quiz, UserQuizResult, LearningProgress
        )
        
        # Tạo tất cả các bảng
        db.create_all()
        
        logger.info("Database đã được khởi tạo thành công")
        
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo database: {str(e)}")
        raise


def get_db_session():
    """
    Lấy database session
    
    Returns:
        Database session
    """
    return db.session


def close_db_session():
    """
    Đóng database session
    """
    db.session.close()


def commit_changes():
    """
    Commit các thay đổi vào database
    """
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Lỗi khi commit database: {str(e)}")
        raise


def rollback_changes():
    """
    Rollback các thay đổi
    """
    db.session.rollback()