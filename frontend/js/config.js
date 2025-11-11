/**
 * Configuration file cho Frontend
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: 'http://localhost:5000/api/v1',
    
    // Endpoints
    ENDPOINTS: {
        // Auth
        REGISTER: '/auth/register',
        LOGIN: '/auth/login',
        LOGOUT: '/auth/logout',
        VERIFY: '/auth/verify',
        ME: '/auth/me',
        
        // Videos
        VIDEOS: '/videos',
        VIDEO_UPLOAD: '/videos/upload',
        VIDEO_DETAIL: '/videos/:id',
        VIDEO_DELETE: '/videos/:id',
        VIDEO_STATUS: '/videos/:id/status',
        
        // Subtitles
        SUBTITLES: '/subtitles/:video_id',
        SUBTITLE_GENERATE: '/subtitles/generate',
        SUBTITLE_DOWNLOAD: '/subtitles/download/:id',
        
        // Quiz
        QUIZ: '/quiz/:video_id',
        QUIZ_SUBMIT: '/quiz/submit',
        QUIZ_RESULTS: '/quiz/results/:user_id',
        
        // Vocabulary
        VOCABULARY: '/vocabulary/:video_id',
        VOCABULARY_SAVE: '/vocabulary/save',
        VOCABULARY_SAVED: '/vocabulary/saved',
        VOCABULARY_DELETE: '/vocabulary/:id',
        
        // Users
        USER_PROFILE: '/users/profile',
        USER_PROGRESS: '/users/progress',
        CHANGE_PASSWORD: '/users/change-password'
    },
    
    // Storage keys
    STORAGE_KEYS: {
        ACCESS_TOKEN: 'access_token',
        USER_DATA: 'user_data',
        THEME: 'theme'
    },
    
    // File upload
    MAX_FILE_SIZE: 500 * 1024 * 1024, // 500MB
    ALLOWED_VIDEO_FORMATS: ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'],
    
    // Pagination
    DEFAULT_PAGE_SIZE: 10,
    
    // Video player
    PLAYBACK_RATES: [0.5, 0.75, 1, 1.25, 1.5, 2],
    
    // Languages
    SUPPORTED_LANGUAGES: {
        'en': 'English',
        'vi': 'Tiếng Việt',
        'ja': '日本語',
        'ko': '한국어',
        'zh': '中文',
        'fr': 'Français',
        'de': 'Deutsch',
        'es': 'Español'
    },
    
    // Status
    VIDEO_STATUS: {
        PENDING: 'pending',
        PROCESSING: 'processing',
        COMPLETED: 'completed',
        FAILED: 'failed'
    },
    
    // Messages
    MESSAGES: {
        SUCCESS: {
            LOGIN: 'Đăng nhập thành công',
            REGISTER: 'Đăng ký thành công',
            UPLOAD: 'Upload video thành công',
            DELETE: 'Xóa thành công',
            SAVE: 'Lưu thành công'
        },
        ERROR: {
            NETWORK: 'Lỗi kết nối mạng',
            UNAUTHORIZED: 'Vui lòng đăng nhập',
            FILE_TOO_LARGE: 'File quá lớn (tối đa 500MB)',
            INVALID_FORMAT: 'Định dạng file không hợp lệ',
            UNKNOWN: 'Đã xảy ra lỗi không mong muốn'
        }
    }
};

// Helper function để build URL
CONFIG.buildUrl = function(endpoint, params = {}) {
    let url = this.API_BASE_URL + endpoint;
    
    // Replace path parameters
    for (const [key, value] of Object.entries(params)) {
        url = url.replace(`:${key}`, value);
    }
    
    return url;
};

// Export config
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}