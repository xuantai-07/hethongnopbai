import getpass

from app import create_app
from app.models import db, Teacher

app = create_app()

with app.app_context():
    username = input("Nhập tên đăng nhập giảng viên: ").strip()

    if not username:
        print("Tên đăng nhập không được để trống.")
        raise SystemExit(1)

    password = getpass.getpass("Nhập mật khẩu: ")
    confirm_password = getpass.getpass("Nhập lại mật khẩu: ")

    if len(password) < 12:
        print("Mật khẩu phải có ít nhất 12 ký tự.")
        raise SystemExit(1)

    if password != confirm_password:
        print("Hai mật khẩu không khớp.")
        raise SystemExit(1)

    teacher = Teacher.query.filter_by(username=username).first()

    if teacher:
        print("Tên đăng nhập này đã tồn tại.")
        raise SystemExit(1)

    teacher = Teacher(username=username)
    teacher.set_password(password)

    db.session.add(teacher)
    db.session.commit()

    print("Đã tạo tài khoản giảng viên thành công.")