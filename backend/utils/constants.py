"""
Constants - Các hằng số sử dụng trong hệ thống
"""

# Video Status
VIDEO_STATUS_PENDING = 'pending'
VIDEO_STATUS_PROCESSING = 'processing'
VIDEO_STATUS_COMPLETED = 'completed'
VIDEO_STATUS_FAILED = 'failed'

VIDEO_STATUSES = [
    VIDEO_STATUS_PENDING,
    VIDEO_STATUS_PROCESSING,
    VIDEO_STATUS_COMPLETED,
    VIDEO_STATUS_FAILED
]

# Learned Status
LEARNED_STATUS_LEARNING = 'learning'
LEARNED_STATUS_LEARNED = 'learned'
LEARNED_STATUS_MASTERED = 'mastered'

LEARNED_STATUSES = [
    LEARNED_STATUS_LEARNING,
    LEARNED_STATUS_LEARNED,
    LEARNED_STATUS_MASTERED
]

# Difficulty Levels
DIFFICULTY_BASIC = 'basic'
DIFFICULTY_INTERMEDIATE = 'intermediate'
DIFFICULTY_ADVANCED = 'advanced'

DIFFICULTY_LEVELS = [
    DIFFICULTY_BASIC,
    DIFFICULTY_INTERMEDIATE,
    DIFFICULTY_ADVANCED
]

# Quiz Difficulty
QUIZ_DIFFICULTY_EASY = 'easy'
QUIZ_DIFFICULTY_MEDIUM = 'medium'
QUIZ_DIFFICULTY_HARD = 'hard'

QUIZ_DIFFICULTIES = [
    QUIZ_DIFFICULTY_EASY,
    QUIZ_DIFFICULTY_MEDIUM,
    QUIZ_DIFFICULTY_HARD
]

# Language Codes
LANGUAGE_ENGLISH = 'en'
LANGUAGE_VIETNAMESE = 'vi'
LANGUAGE_JAPANESE = 'ja'
LANGUAGE_KOREAN = 'ko'
LANGUAGE_CHINESE = 'zh'
LANGUAGE_FRENCH = 'fr'
LANGUAGE_GERMAN = 'de'
LANGUAGE_SPANISH = 'es'
LANGUAGE_AUTO = 'auto'

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'vi': 'Tiếng Việt',
    'ja': '日本語',
    'ko': '한국어',
    'zh': '中文',
    'fr': 'Français',
    'de': 'Deutsch',
    'es': 'Español'
}

# File Extensions
VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv']
AUDIO_EXTENSIONS = ['mp3', 'wav', 'aac', 'm4a']
SUBTITLE_EXTENSIONS = ['srt', 'vtt']

# Subtitle Formats
SUBTITLE_FORMAT_SRT = 'srt'
SUBTITLE_FORMAT_VTT = 'vtt'

# Part of Speech
POS_NOUN = 'noun'
POS_VERB = 'verb'
POS_ADJECTIVE = 'adjective'
POS_ADVERB = 'adverb'
POS_PRONOUN = 'pronoun'
POS_PREPOSITION = 'preposition'
POS_CONJUNCTION = 'conjunction'
POS_INTERJECTION = 'interjection'

PARTS_OF_SPEECH = [
    POS_NOUN,
    POS_VERB,
    POS_ADJECTIVE,
    POS_ADVERB,
    POS_PRONOUN,
    POS_PREPOSITION,
    POS_CONJUNCTION,
    POS_INTERJECTION
]

# Error Messages
ERROR_INVALID_CREDENTIALS = 'Tên đăng nhập hoặc mật khẩu không đúng'
ERROR_USER_EXISTS = 'Tên đăng nhập hoặc email đã tồn tại'
ERROR_USER_NOT_FOUND = 'Người dùng không tồn tại'
ERROR_VIDEO_NOT_FOUND = 'Video không tồn tại'
ERROR_UNAUTHORIZED = 'Không có quyền truy cập'
ERROR_INVALID_TOKEN = 'Token không hợp lệ'
ERROR_EXPIRED_TOKEN = 'Token đã hết hạn'
ERROR_FILE_TOO_LARGE = 'File quá lớn'
ERROR_INVALID_FILE_TYPE = 'Định dạng file không được hỗ trợ'
ERROR_PROCESSING_FAILED = 'Xử lý video thất bại'

# Success Messages
SUCCESS_REGISTER = 'Đăng ký thành công'
SUCCESS_LOGIN = 'Đăng nhập thành công'
SUCCESS_LOGOUT = 'Đăng xuất thành công'
SUCCESS_VIDEO_UPLOAD = 'Upload video thành công'
SUCCESS_VIDEO_DELETE = 'Xóa video thành công'
SUCCESS_SUBTITLE_GENERATED = 'Tạo phụ đề thành công'
SUCCESS_VOCABULARY_SAVED = 'Lưu từ vựng thành công'
SUCCESS_QUIZ_SUBMITTED = 'Nộp bài quiz thành công'

# Pagination
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000

# File Size Limits (bytes)
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100MB

# Processing Settings
MAX_VIDEO_DURATION = 2 * 60 * 60  # 2 hours in seconds
MIN_VIDEO_DURATION = 10  # 10 seconds
MAX_VOCABULARY_PER_VIDEO = 100
MIN_WORD_LENGTH = 3
QUIZ_QUESTIONS_PER_VIDEO = 10
QUIZ_OPTIONS_COUNT = 4

# Whisper Settings
WHISPER_MODELS = ['tiny', 'base', 'small', 'medium', 'large']
WHISPER_DEFAULT_MODEL = 'medium'
WHISPER_DEVICES = ['cpu', 'cuda']
WHISPER_COMPUTE_TYPES = ['int8', 'float16', 'float32']

# Cache Settings
CACHE_TIMEOUT = 3600  # 1 hour
CACHE_KEY_PREFIX = 'video_subtitle_'

# Logging Levels
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'
LOG_LEVEL_CRITICAL = 'CRITICAL'