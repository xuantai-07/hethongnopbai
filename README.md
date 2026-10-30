# Hệ Thống Giao và Thu Bài Sinh Viên

Ứng dụng web viết bằng **Flask + SQLite** hỗ trợ giảng viên giao đề bài, thu bài nộp của sinh viên, quản lý phiên bản nộp bài, xuất bảng điểm/danh sách Excel và tải toàn bộ bài làm dưới dạng gói ZIP.

---

## Tính năng chính

### Dành cho sinh viên
- Xem danh sách bài tập đang mở và chưa quá hạn, tải tệp đề bài trực tiếp.
- Nộp bài với kiểm tra định dạng & dung lượng ngay trên trình duyệt lẫn máy chủ (tối đa **20 MB**).
- Giữ nguyên tên tệp tiếng Việt có dấu khi hiển thị và tải về, đồng thời lưu trữ an toàn trên đĩa bằng tên UUID.
- Chống nộp lặp khi bấm F5 (Post/Redirect/Get) và giữ lại dữ liệu đã nhập nếu biểu mẫu báo lỗi.

### Dành cho giảng viên
- Tạo, chỉnh sửa, đóng/mở và xóa bài tập (kèm xác nhận an toàn trước khi đóng hoặc xóa).
- Theo dõi lịch sử nộp bài có **phân trang**, **lọc theo bài tập**, và tự động đánh dấu bản **Mới nhất / Bản cũ** cho từng sinh viên.
- **Xuất danh sách ra Excel (`.xlsx`)** theo bộ lọc hiện tại.
- **Tải toàn bộ bài nộp thành tệp ZIP** (tùy chọn lấy tất cả các lần nộp hoặc chỉ lấy bản mới nhất của mỗi sinh viên).

### Bảo mật & Hiệu năng
- Bảo vệ biểu mẫu bằng CSRF token (không giới hạn thời gian sống trong phiên làm việc), mật khẩu giảng viên băm an toàn bằng Werkzeug.
- Giới hạn tần suất (Rate Limiting) cho cả thao tác nộp bài và đăng nhập sai.
- SQLite cấu hình chế độ **WAL (Write-Ahead Logging)**, `busy_timeout=5000`, chỉ mục tối ưu và truy vấn gom nhóm (`joinedload` / `GROUP BY`) loại bỏ lỗi N+1.

---

## Cài đặt và Khởi chạy

### 1. Cài đặt thư viện
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Cấu hình biến môi trường (tùy chọn)
Tạo tệp `.env` ở thư mục gốc nếu muốn tùy chỉnh cấu hình (nếu không đặt `SECRET_KEY`, hệ thống sẽ tự sinh và lưu khóa bền vững vào `data/.secret_key`):
```env
SECRET_KEY=khoa-bi-mat-ngau-nhien-cua-ban
HOST=0.0.0.0
PORT=5000
WAITRESS_THREADS=8
SUBMISSIONS_PER_PAGE=20
TRUST_PROXY_COUNT=0
SESSION_COOKIE_SECURE=0
```
*(Nếu đặt ứng dụng sau 1 lớp Nginx/Caddy/Cloudflare có HTTPS, hãy đặt `TRUST_PROXY_COUNT=1` và `SESSION_COOKIE_SECURE=1`).*

### 3. Tạo tài khoản giảng viên
```powershell
python create_teacher.py
```
*(Mật khẩu yêu cầu tối thiểu 12 ký tự).*

### 4. Chạy máy chủ (Waitress WSGI)
```powershell
python run.py
```
Truy cập:
- Trang sinh viên nộp bài: `http://localhost:5000/`
- Trang giảng viên: `http://localhost:5000/teacher`

---

## Quản lý Cơ sở dữ liệu & Sao lưu

### Quản lý schema với Flask-Migrate
```powershell
flask --app run.py db init
flask --app run.py db migrate -m "Initial schema"
flask --app run.py db upgrade
```
*(Nếu nâng cấp từ cơ sở dữ liệu cũ trước khi có cột tệp đề bài, có thể chạy `python migrate_db.py`).*

### Sao lưu dữ liệu tự động
Chạy lệnh sau để sao lưu nóng CSDL SQLite cùng toàn bộ tệp đề bài và bài nộp vào thư mục `backups/`:
```powershell
python backup.py --keep 10
```

