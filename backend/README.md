# Backend - Hệ thống trích xuất phụ đề và dịch thuật video

Backend API cho hệ thống trích xuất phụ đề và dịch thuật video tự động sử dụng AI.

## Yêu cầu hệ thống

- Python 3.11.9
- SQL Server 2019 hoặc mới hơn
- FFmpeg (cho xử lý video/audio)
- 8GB RAM trở lên (cho Whisper model)

## Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt FFmpeg

**Windows:**
- Download từ: https://ffmpeg.org/download.html
- Thêm vào PATH

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. Cài đặt ODBC Driver cho SQL Server

**Windows:**
- Download từ: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

**Linux:**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### 4. Cấu hình Database

1. Tạo database trong SQL Server:
```sql
CREATE DATABASE VideoSubtitleDB;
```

2. Chạy script tạo bảng:
```bash
# Trong SQL Server Management Studio, chạy file:
database/schema.sql
```

### 5. Cấu hình môi trường

1. Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

2. Chỉnh sửa file `.env` với thông tin của bạn:
```env
# Database
DB_SERVER=localhost
DB_NAME=VideoSubtitleDB
DB_USERNAME=sa
DB_PASSWORD=your_password

# OpenAI API Key
OPENAI_API_KEY=your_api_key_here

# JWT Secret
JWT_SECRET_KEY=your_secret_key_here
SECRET_KEY=your_flask_secret_key
```

## Chạy ứng dụng

### Development mode

```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:5000`

### Production mode

```bash
# Sử dụng Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Hoặc sử dụng Waitress (Windows)
waitress-serve --port=5000 app:app
```

## Cấu trúc API

### Base URL
```
http://localhost:5000/api/v1
```

### Endpoints chính

#### Authentication
- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập
- `POST /auth/logout` - Đăng xuất
- `GET /auth/verify` - Xác thực token

#### Videos
- `GET /videos` - Lấy danh sách video
- `POST /videos/upload` - Upload video
- `GET /videos/:id` - Chi tiết video
- `DELETE /videos/:id` - Xóa video
- `GET /videos/:id/status` - Trạng thái xử lý

#### Subtitles
- `GET /subtitles/:video_id` - Lấy phụ đề
- `POST /subtitles/generate` - Tạo phụ đề
- `GET /subtitles/download/:id` - Tải phụ đề

#### Quiz
- `GET /quiz/:video_id` - Lấy quiz
- `POST /quiz/submit` - Nộp bài quiz
- `GET /quiz/results/:user_id` - Kết quả quiz

#### Vocabulary
- `GET /vocabulary/:video_id` - Từ vựng trong video
- `POST /vocabulary/save` - Lưu từ vựng
- `GET /vocabulary/saved` - Từ vựng đã lưu
- `DELETE /vocabulary/:id` - Xóa từ vựng

#### Users
- `GET /users/profile` - Thông tin profile
- `PUT /users/profile` - Cập nhật profile
- `GET /users/progress` - Tiến trình học
- `POST /users/progress` - Cập nhật tiến trình

## Testing

```bash
# Chạy tests
pytest

# Chạy với coverage
pytest --cov=.
```

## Troubleshooting

### Lỗi kết nối SQL Server
- Kiểm tra SQL Server đã chạy
- Kiểm tra firewall cho phép port 1433
- Kiểm tra ODBC Driver đã cài đặt đúng

### Lỗi Whisper model
- Đảm bảo có đủ RAM (8GB+)
- Model sẽ tự động download lần đầu chạy
- Kiểm tra kết nối internet

### Lỗi FFmpeg
- Kiểm tra FFmpeg đã cài đặt: `ffmpeg -version`
- Kiểm tra FFmpeg có trong PATH

## Logs

Logs được lưu tại: `logs/app.log`

## Bảo mật

- Luôn sử dụng HTTPS trong production
- Thay đổi SECRET_KEY và JWT_SECRET_KEY
- Không commit file `.env` vào git
- Sử dụng strong password cho database

## Tác giả

Đồ án tốt nghiệp - Hệ thống trích xuất phụ đề và dịch thuật video