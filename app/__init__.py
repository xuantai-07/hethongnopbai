from flask import Flask, flash, redirect, request, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from sqlalchemy import event, text
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from app.models import db, Teacher

login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


@login_manager.user_loader
def load_teacher(user_id):
    return db.session.get(Teacher, int(user_id))


def _redirect_back():
    """Quay lại trang phù hợp sau khi gặp lỗi (không dùng Referer để tránh open redirect)."""
    if request.endpoint == "main.teacher_login":
        return redirect(url_for("main.teacher_login"))
    if request.path.startswith("/teacher"):
        return redirect(url_for("main.teacher_dashboard"))
    return redirect(url_for("main.index"))


def register_error_handlers(app):
    @app.errorhandler(413)
    def file_too_large(error):
        max_mb = app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024)
        flash(
            f"Tệp quá lớn. Dung lượng tối đa cho mỗi lần tải lên là {max_mb} MB.",
            "error"
        )
        return _redirect_back()

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        flash(
            "Phiên làm việc đã hết hạn hoặc không hợp lệ. "
            "Vui lòng thực hiện lại.",
            "error"
        )
        return _redirect_back()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Hỗ trợ lấy IP thật (X-Forwarded-For) và HTTPS khi chạy sau Reverse Proxy
    proxy_count = app.config.get("TRUST_PROXY_COUNT", 0)
    if proxy_count > 0:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=proxy_count,
            x_proto=proxy_count,
            x_host=proxy_count,
        )

    # Khởi tạo cơ sở dữ liệu & Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Khởi tạo đăng nhập giảng viên
    login_manager.init_app(app)
    login_manager.login_view = "main.teacher_login"
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."

    # Bảo vệ biểu mẫu bằng CSRF
    csrf.init_app(app)

    # Trang báo lỗi thân thiện (tệp quá lớn, CSRF hết hạn)
    register_error_handlers(app)

    @app.after_request
    def _set_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault(
            "Referrer-Policy", "strict-origin-when-cross-origin"
        )
        return response

    # Đăng ký các đường dẫn của ứng dụng
    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        # ── Nhóm 2.1: Bật WAL, synchronous=NORMAL, foreign_keys và busy_timeout ──
        @event.listens_for(db.engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, _connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

        # Tạo các bảng nếu chưa tồn tại
        db.create_all()

        # ── Nhóm 2.4: Tạo index cho cơ sở dữ liệu đã có ──
        with db.engine.begin() as conn:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_sub_assignment_student "
                "ON submissions(assignment_id, student_code)"
            ))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_sub_submitted_at "
                "ON submissions(submitted_at)"
            ))

    return app
