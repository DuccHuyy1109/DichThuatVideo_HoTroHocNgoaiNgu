"""
Database Models - UPDATED WITH VIDEO_ID IN VOCABULARY
Định nghĩa các bảng trong database
"""
from datetime import datetime
from database.db_config import db


class User(db.Model):
    """Bảng người dùng"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    videos = db.relationship('Video', backref='user', lazy=True, cascade='all, delete-orphan')
    vocabularies = db.relationship('UserVocabulary', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_results = db.relationship('UserQuizResult', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_progress = db.relationship('LearningProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }


class Video(db.Model):
    """Bảng video"""
    __tablename__ = 'videos'
    
    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.Float)
    language_detected = db.Column(db.String(10))
    status = db.Column(db.String(20), default='pending')
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    
    # Relationships
    subtitles = db.relationship('Subtitle', backref='video', lazy=True, cascade='all, delete-orphan')
    vocabularies = db.relationship('Vocabulary', backref='video', lazy=True, cascade='all, delete-orphan')  # ✅ NEW
    quizzes = db.relationship('Quiz', backref='video', lazy=True, cascade='all, delete-orphan')
    learning_progress = db.relationship('LearningProgress', backref='video', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'video_id': self.video_id,
            'user_id': self.user_id,
            'title': self.title,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'duration': self.duration,
            'language_detected': self.language_detected,
            'status': self.status,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None
        }


class Subtitle(db.Model):
    """Bảng phụ đề"""
    __tablename__ = 'subtitles'
    
    subtitle_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(500))
    subtitle_format = db.Column(db.String(10), default='srt')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'subtitle_id': self.subtitle_id,
            'video_id': self.video_id,
            'language': self.language,
            'content': self.content,
            'file_path': self.file_path,
            'subtitle_format': self.subtitle_format,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Vocabulary(db.Model):
    """Bảng từ vựng - ✅ UPDATED WITH VIDEO_ID"""
    __tablename__ = 'vocabulary'
    
    vocab_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'))  # ✅ NEW: Link to video
    word = db.Column(db.String(100), nullable=False, index=True)
    translation = db.Column(db.String(255), nullable=False)
    pronunciation = db.Column(db.String(100))
    example_sentence = db.Column(db.Text)
    example_translation = db.Column(db.Text)
    language = db.Column(db.String(10), nullable=False)
    part_of_speech = db.Column(db.String(20))
    difficulty_level = db.Column(db.String(20))
    
    # Relationships
    user_vocabularies = db.relationship('UserVocabulary', backref='vocabulary', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'vocab_id': self.vocab_id,
            'video_id': self.video_id,  # ✅ NEW
            'word': self.word,
            'translation': self.translation,
            'pronunciation': self.pronunciation,
            'example_sentence': self.example_sentence,
            'example_translation': self.example_translation,
            'language': self.language,
            'part_of_speech': self.part_of_speech,
            'difficulty_level': self.difficulty_level
        }


class UserVocabulary(db.Model):
    """Bảng từ vựng cá nhân của user"""
    __tablename__ = 'user_vocabulary'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    vocab_id = db.Column(db.Integer, db.ForeignKey('vocabulary.vocab_id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'))
    learned_status = db.Column(db.String(20), default='learning')
    saved_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime)
    review_count = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vocab_id': self.vocab_id,
            'video_id': self.video_id,
            'learned_status': self.learned_status,
            'saved_date': self.saved_date.isoformat() if self.saved_date else None,
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None,
            'review_count': self.review_count
        }


class Quiz(db.Model):
    """Bảng quiz"""
    __tablename__ = 'quizzes'
    
    quiz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    wrong_answer_1 = db.Column(db.String(255), nullable=False)
    wrong_answer_2 = db.Column(db.String(255), nullable=False)
    wrong_answer_3 = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_results = db.relationship('UserQuizResult', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'quiz_id': self.quiz_id,
            'video_id': self.video_id,
            'question': self.question,
            'correct_answer': self.correct_answer,
            'wrong_answer_1': self.wrong_answer_1,
            'wrong_answer_2': self.wrong_answer_2,
            'wrong_answer_3': self.wrong_answer_3,
            'explanation': self.explanation,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserQuizResult(db.Model):
    """Bảng kết quả quiz của user"""
    __tablename__ = 'user_quiz_results'
    
    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_taken = db.Column(db.Integer)
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'result_id': self.result_id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'selected_answer': self.selected_answer,
            'is_correct': self.is_correct,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken': self.time_taken
        }


class LearningProgress(db.Model):
    """Bảng tiến trình học tập"""
    __tablename__ = 'learning_progress'
    
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.video_id'), nullable=False)
    watch_duration = db.Column(db.Float, default=0)
    completion_percentage = db.Column(db.Float, default=0)
    last_watched = db.Column(db.DateTime, default=datetime.utcnow)
    watch_count = db.Column(db.Integer, default=1)
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'progress_id': self.progress_id,
            'user_id': self.user_id,
            'video_id': self.video_id,
            'watch_duration': self.watch_duration,
            'completion_percentage': self.completion_percentage,
            'last_watched': self.last_watched.isoformat() if self.last_watched else None,
            'watch_count': self.watch_count
        }