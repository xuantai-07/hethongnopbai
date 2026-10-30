import os
import secrets
from pathlib import Path

# Thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent

# Đọc biến môi trường từ tệp .env (nếu có)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# Dữ liệu được lưu ngoài thư mục chứa mã nguồn
DATA_DIR = Path(
    os.environ.get("HE_THONG_NOP_BAI_DATA", BASE_DIR / "data")
).resolve()

# Thư mục lưu các tệp sinh viên nộp
UPLOAD_DIR = DATA_DIR / "submissions"
ASSIGNMENT_DIR = DATA_DIR / "assignment_files"

# Tạo thư mục dữ liệu nếu chưa tồn tại
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ASSIGNMENT_DIR.mkdir(parents=True, exist_ok=True)


def _load_secret_key():
    """Ưu tiên SECRET_KEY từ biến môi trường / .env.

    Nếu không có, tự sinh một khóa ngẫu nhiên và lưu vào DATA_DIR/.secret_key
    để giữ nguyên giữa các lần khởi động (không dùng khóa viết cứng trong mã).
    """
    key = os.environ.get("SECRET_KEY", "").strip()
    if key:
        return key

    key_file = DATA_DIR / ".secret_key"
    if key_file.exists():
        key = key_file.read_text(encoding="utf-8").strip()
        if key:
            return key

    key = secrets.token_hex(32)
    key_file.write_text(key, encoding="utf-8")
    return key


class Config:
    SECRET_KEY = _load_secret_key()

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{(DATA_DIR / 'nopbai.db').as_posix()}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # Tối đa 20 MB mỗi yêu cầu
    UPLOAD_FOLDER = str(UPLOAD_DIR)
    ASSIGNMENT_FOLDER = str(ASSIGNMENT_DIR)

    # Token CSRF không hết hạn theo thời gian (vẫn gắn với phiên trình duyệt),
    # tránh lỗi khi sinh viên mở trang làm bài lâu rồi mới nộp.
    WTF_CSRF_TIME_LIMIT = None

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "0").strip() == "1"
    )

    # Số lớp Reverse Proxy đứng trước ứng dụng (0 = chạy trực tiếp, 1 = sau Nginx/Cloudflare)
    TRUST_PROXY_COUNT = int(os.environ.get("TRUST_PROXY_COUNT", 0))

    # Chống spam nộp bài (chỉ tính các lần nộp thành công)
    SUBMIT_LIMIT_WINDOW = int(os.environ.get("SUBMIT_LIMIT_WINDOW", 600))  # giây
    SUBMIT_LIMIT_PER_IP = int(os.environ.get("SUBMIT_LIMIT_PER_IP", 30))
    SUBMIT_LIMIT_PER_STUDENT = int(
        os.environ.get("SUBMIT_LIMIT_PER_STUDENT", 5)
    )

    # Giới hạn đăng nhập sai (nhóm 1.4)
    LOGIN_LIMIT_WINDOW = int(os.environ.get("LOGIN_LIMIT_WINDOW", 600))   # 10 phút
    LOGIN_LIMIT_PER_IP = int(os.environ.get("LOGIN_LIMIT_PER_IP", 5))

    # Phân trang (nhóm 2.3)
    SUBMISSIONS_PER_PAGE = int(os.environ.get("SUBMISSIONS_PER_PAGE", 20))