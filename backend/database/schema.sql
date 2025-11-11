-- Database Schema cho SQL Server
-- Hệ thống trích xuất phụ đề và dịch thuật video

-- Tạo database
CREATE DATABASE VideoSubtitleDB;
GO

USE VideoSubtitleDB;
GO

-- Bảng Users (Người dùng)
CREATE TABLE users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) NOT NULL UNIQUE,
    email NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(100),
    created_at DATETIME DEFAULT GETDATE(),
    last_login DATETIME,
    is_active BIT DEFAULT 1
);

-- Index cho users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Bảng Videos (Video đã upload)
CREATE TABLE videos (
    video_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    title NVARCHAR(255) NOT NULL,
    original_filename NVARCHAR(255) NOT NULL,
    file_path NVARCHAR(500) NOT NULL,
    duration FLOAT,
    language_detected NVARCHAR(10),
    status NVARCHAR(20) DEFAULT 'pending',
    upload_date DATETIME DEFAULT GETDATE(),
    processed_date DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Index cho videos
CREATE INDEX idx_videos_user_id ON videos(user_id);
CREATE INDEX idx_videos_status ON videos(status);

-- Bảng Subtitles (Phụ đề)
CREATE TABLE subtitles (
    subtitle_id INT PRIMARY KEY IDENTITY(1,1),
    video_id INT NOT NULL,
    language NVARCHAR(10) NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    file_path NVARCHAR(500),
    subtitle_format NVARCHAR(10) DEFAULT 'srt',
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- Index cho subtitles
CREATE INDEX idx_subtitles_video_id ON subtitles(video_id);
CREATE INDEX idx_subtitles_language ON subtitles(language);

-- Bảng Vocabulary (Từ vựng)
CREATE TABLE vocabulary (
    vocab_id INT PRIMARY KEY IDENTITY(1,1),
    word NVARCHAR(100) NOT NULL,
    translation NVARCHAR(255) NOT NULL,
    pronunciation NVARCHAR(100),
    example_sentence NVARCHAR(MAX),
    example_translation NVARCHAR(MAX),
    language NVARCHAR(10) NOT NULL,
    part_of_speech NVARCHAR(20),
    difficulty_level NVARCHAR(20)
);

-- Index cho vocabulary
CREATE INDEX idx_vocabulary_word ON vocabulary(word);
CREATE INDEX idx_vocabulary_language ON vocabulary(language);

-- Bảng UserVocabulary (Từ vựng cá nhân)
CREATE TABLE user_vocabulary (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    vocab_id INT NOT NULL,
    video_id INT,
    learned_status NVARCHAR(20) DEFAULT 'learning',
    saved_date DATETIME DEFAULT GETDATE(),
    last_reviewed DATETIME,
    review_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (vocab_id) REFERENCES vocabulary(vocab_id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE SET NULL
);

-- Index cho user_vocabulary
CREATE INDEX idx_user_vocabulary_user_id ON user_vocabulary(user_id);
CREATE INDEX idx_user_vocabulary_vocab_id ON user_vocabulary(vocab_id);

-- Bảng Quizzes (Quiz)
CREATE TABLE quizzes (
    quiz_id INT PRIMARY KEY IDENTITY(1,1),
    video_id INT NOT NULL,
    question NVARCHAR(MAX) NOT NULL,
    correct_answer NVARCHAR(255) NOT NULL,
    wrong_answer_1 NVARCHAR(255) NOT NULL,
    wrong_answer_2 NVARCHAR(255) NOT NULL,
    wrong_answer_3 NVARCHAR(255) NOT NULL,
    explanation NVARCHAR(MAX),
    difficulty_level NVARCHAR(20) DEFAULT 'medium',
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- Index cho quizzes
CREATE INDEX idx_quizzes_video_id ON quizzes(video_id);

-- Bảng UserQuizResults (Kết quả quiz)
CREATE TABLE user_quiz_results (
    result_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    quiz_id INT NOT NULL,
    selected_answer NVARCHAR(255) NOT NULL,
    is_correct BIT NOT NULL,
    completed_at DATETIME DEFAULT GETDATE(),
    time_taken INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE
);

-- Index cho user_quiz_results
CREATE INDEX idx_user_quiz_results_user_id ON user_quiz_results(user_id);
CREATE INDEX idx_user_quiz_results_quiz_id ON user_quiz_results(quiz_id);

-- Bảng LearningProgress (Tiến trình học)
CREATE TABLE learning_progress (
    progress_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    video_id INT NOT NULL,
    watch_duration FLOAT DEFAULT 0,
    completion_percentage FLOAT DEFAULT 0,
    last_watched DATETIME DEFAULT GETDATE(),
    watch_count INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES videos(video_id) ON DELETE CASCADE
);

-- Index cho learning_progress
CREATE INDEX idx_learning_progress_user_id ON learning_progress(user_id);
CREATE INDEX idx_learning_progress_video_id ON learning_progress(video_id);

GO