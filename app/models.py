from datetime import datetime
from typing import TYPE_CHECKING, Any

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class BaseModel(db.Model):
    """Lớp cơ sở chung cho các model."""

    __abstract__ = True

    if TYPE_CHECKING:
        # Flask-SQLAlchemy không khai báo kiểu cho hàm khởi tạo của db.Model,
        # nên Pyrefly/Pylance hiểu nhầm là object.__init__() và báo lỗi
        # "Unexpected keyword argument". Khai báo lại (chỉ dùng khi kiểm tra kiểu).
        def __init__(self, **kwargs: Any) -> None: ...


class Teacher(UserMixin, BaseModel):
    """Tài khoản giảng viên."""

    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Assignment(BaseModel):
    """Bài tập do giảng viên tạo."""

    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    # Mô tả ngắn, không bắt buộc
    description = db.Column(db.Text, default="")

    # Thông tin tệp đề bài
    assignment_original_filename = db.Column(db.String(255), nullable=True)
    assignment_stored_filename = db.Column(
        db.String(255), unique=True, nullable=True
    )

    deadline = db.Column(db.DateTime, nullable=True)
    is_open = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)


class Submission(BaseModel):
    """Một lần nộp bài của sinh viên."""

    __tablename__ = "submissions"

    # Index cho truy vấn thường dùng (nhóm 2.4)
    __table_args__ = (
        db.Index(
            "idx_sub_assignment_student",
            "assignment_id", "student_code",
        ),
        db.Index("idx_sub_submitted_at", "submitted_at"),
    )

    id = db.Column(db.Integer, primary_key=True)

    assignment_id = db.Column(
        db.Integer,
        db.ForeignKey("assignments.id"),
        nullable=False
    )

    student_name = db.Column(db.String(150), nullable=False)
    student_number = db.Column(db.String(50), nullable=False)
    student_code = db.Column(db.String(50), nullable=False)

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False)

    submitted_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    assignment = db.relationship(
        "Assignment",
        backref=db.backref("submissions", lazy=True)
    )