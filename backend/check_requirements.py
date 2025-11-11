"""
Script kiểm tra các thư viện trong requirements.txt đã được cài đặt chưa
Chạy: python check_requirements.py
"""
import subprocess
import sys

# Danh sách thư viện cần kiểm tra
requirements = [
    # Web Framework
    'Flask==3.0.0',
    'Flask-CORS==4.0.0',
    'Flask-JWT-Extended==4.6.0',
    'Werkzeug==3.0.1',
    
    # Database
    'pyodbc==5.0.1',
    'SQLAlchemy==2.0.23',
    
    # AI/ML - Speech to Text
    'openai-whisper==20231117',
    'faster-whisper==0.10.0',
    'torch==2.1.2',
    'torchaudio==2.1.2',
    
    # OpenAI GPT-4 / GPT-4o
    'openai==1.42.0',
    
    # Video/Audio Processing
    'moviepy==2.1.1',
    'pydub==0.25.1',
    'ffmpeg-python==0.2.0',
    
    # Subtitle Processing
    'pysrt==1.1.2',
    'webvtt-py==0.4.6',
    
    # Language Detection
    'langdetect==1.0.9',
    'pycountry==23.12.11',
    
    # Utilities
    'python-dotenv==1.0.0',
    'requests==2.31.0',
    'Pillow==10.1.0',
    
    # Validation
    'email-validator==2.1.0',
    'python-multipart==0.0.6',
    
    # Security
    'bcrypt==4.1.2',
    'cryptography==41.0.7',
    
    # File handling
    'python-magic==0.4.27',
    
    # Date/Time
    'python-dateutil==2.8.2',
    'pytz==2023.3',
    
    # Progress tracking
    'tqdm==4.66.1',
    
    # JSON handling
    'ujson==5.9.0',
    
    # HTTP client
    'httpx==0.25.2',
    
    # Development / Testing
    'pytest==7.4.3',
    'pytest-flask==1.3.0',
    'python-json-logger==2.0.7',
    'av==11.0.0'
]

def get_installed_packages():
    """Lấy danh sách các package đã cài"""
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'list'],
        capture_output=True,
        text=True
    )
    
    installed = {}
    lines = result.stdout.strip().split('\n')[2:]  # Skip header
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0].lower().replace('_', '-')
            version = parts[1]
            installed[name] = version
    
    return installed

def check_requirements():
    """Kiểm tra từng requirement"""
    print("=" * 80)
    print("KIỂM TRA CÁC THƯ VIỆN TRONG REQUIREMENTS.TXT")
    print("=" * 80)
    print()
    
    installed = get_installed_packages()
    
    missing = []
    wrong_version = []
    installed_correct = []
    
    for req in requirements:
        # Parse requirement
        if '==' in req:
            package, version = req.split('==')
        else:
            package = req
            version = None
        
        package_key = package.lower().replace('_', '-')
        
        # Kiểm tra đã cài chưa
        if package_key in installed:
            installed_version = installed[package_key]
            if version and installed_version != version:
                wrong_version.append((package, version, installed_version))
                print(f"⚠️  {package:<30} Cần: {version:<15} Đã cài: {installed_version}")
            else:
                installed_correct.append((package, installed_version))
                print(f"✅ {package:<30} {installed_version}")
        else:
            missing.append((package, version))
            print(f"❌ {package:<30} CHƯA CÀI (cần: {version})")
    
    # Tổng kết
    print()
    print("=" * 80)
    print("TỔNG KẾT:")
    print("=" * 80)
    print(f"✅ Đã cài đúng:        {len(installed_correct)}/{len(requirements)}")
    print(f"⚠️  Sai version:       {len(wrong_version)}/{len(requirements)}")
    print(f"❌ Chưa cài:           {len(missing)}/{len(requirements)}")
    print()
    
    # In danh sách thiếu
    if missing:
        print("=" * 80)
        print("CÁC THƯ VIỆN CHƯA CÀI:")
        print("=" * 80)
        for package, version in missing:
            if version:
                print(f"pip install {package}=={version}")
            else:
                print(f"pip install {package}")
        print()
    
    # In danh sách sai version
    if wrong_version:
        print("=" * 80)
        print("CÁC THƯ VIỆN SAI VERSION (CẦN CẬP NHẬT):")
        print("=" * 80)
        for package, needed, current in wrong_version:
            print(f"pip install {package}=={needed}  # Hiện tại: {current}")
        print()
    
    # Lệnh cài đặt nhanh
    if missing or wrong_version:
        print("=" * 80)
        print("LỆNH CÀI ĐẶT NHANH:")
        print("=" * 80)
        print("pip install -r requirements.txt")
        print()
        print("HOẶC:")
        print("pip install --upgrade -r requirements.txt")
        print()

if __name__ == "__main__":
    check_requirements()