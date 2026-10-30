from sqlalchemy import inspect, text

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)

    if "assignments" not in inspector.get_table_names():
        print("Chưa tìm thấy bảng assignments.")
        raise SystemExit(1)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("assignments")
    }

    migrations = {
        "assignment_original_filename":
            "ALTER TABLE assignments "
            "ADD COLUMN assignment_original_filename VARCHAR(255)",

        "assignment_stored_filename":
            "ALTER TABLE assignments "
            "ADD COLUMN assignment_stored_filename VARCHAR(255)",
    }

    with db.engine.begin() as connection:
        for column_name, sql in migrations.items():
            if column_name not in existing_columns:
                connection.execute(text(sql))
                print(f"Đã thêm cột: {column_name}")
            else:
                print(f"Cột đã tồn tại: {column_name}")

    print("Cập nhật cơ sở dữ liệu hoàn tất.")