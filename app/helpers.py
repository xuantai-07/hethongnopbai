import re
import threading
import time
import unicodedata
from collections import defaultdict, deque


# ---------------------------------------------------------------------------
# Xử lý tên tệp
# ---------------------------------------------------------------------------

# Ký tự điều khiển và ký tự không hợp lệ trong tên tệp (Windows/Linux)
_INVALID_FILENAME_CHARS = re.compile(r'[\x00-\x1f\x7f<>:"/\\|?*]')


def clean_display_filename(filename, max_length=200):
    """Làm sạch tên tệp gốc để hiển thị / làm tên khi tải về.

    Khác với secure_filename, hàm này GIỮ NGUYÊN tiếng Việt có dấu.
    Tên này KHÔNG dùng để lưu trên đĩa (tệp lưu bằng tên UUID).
    """
    name = unicodedata.normalize("NFC", filename or "")

    # Bỏ phần đường dẫn nếu trình duyệt gửi kèm (ví dụ: C:\fakepath\a.pdf)
    name = name.replace("\\", "/").rsplit("/", 1)[-1]

    name = _INVALID_FILENAME_CHARS.sub("_", name)
    name = " ".join(name.split()).strip(" .")

    if len(name) > max_length:
        stem, dot, ext = name.rpartition(".")
        if dot and 0 < len(ext) <= 10:
            name = f"{stem[:max_length - len(ext) - 1]}.{ext}"
        else:
            name = name[:max_length]

    return name


def get_extension(filename):
    """Trả về phần mở rộng (chữ thường, không có dấu chấm) hoặc chuỗi rỗng."""
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


# ---------------------------------------------------------------------------
# Giới hạn tần suất (in-memory, an toàn đa luồng)
# ---------------------------------------------------------------------------

class RateLimiter:
    """Bộ đếm cửa sổ trượt đơn giản, lưu trong bộ nhớ.

    Phù hợp khi chạy 1 tiến trình (Flask dev server hoặc waitress).
    Nếu chạy nhiều tiến trình cần chuyển sang Redis / Flask-Limiter.
    """

    _CLEANUP_THRESHOLD = 10_000

    def __init__(self):
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key, window, now):
        hits = self._hits.get(key)
        if hits is None:
            return None
        while hits and now - hits[0] >= window:
            hits.popleft()
        if not hits:
            del self._hits[key]
            return None
        return hits

    def is_limited(self, key, limit, window):
        """True nếu key đã đạt giới hạn `limit` lần trong `window` giây."""
        now = time.monotonic()
        with self._lock:
            hits = self._prune(key, window, now)
            return hits is not None and len(hits) >= limit

    def hit(self, key, window):
        """Ghi nhận thêm một lần cho key."""
        now = time.monotonic()
        with self._lock:
            self._prune(key, window, now)
            self._hits[key].append(now)

            # Dọn các key cũ để bộ nhớ không tăng mãi
            if len(self._hits) > self._CLEANUP_THRESHOLD:
                for stale_key in list(self._hits):
                    self._prune(stale_key, window, now)

    def reset(self, key):
        with self._lock:
            self._hits.pop(key, None)


rate_limiter = RateLimiter()
