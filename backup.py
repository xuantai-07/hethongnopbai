"""Script sao lưu tự động cơ sở dữ liệu SQLite và các tệp đính kèm.

Sử dụng sqlite3.Connection.backup() để sao lưu an toàn ngay cả khi
ứng dụng đang chạy ở chế độ WAL, sau đó nén toàn bộ CSDL cùng thư mục
bài nộp và đề bài thành một tệp ZIP có gắn nhãn thời gian.

Cách dùng:
    python backup.py
    python backup.py --output-dir backups --keep 10
"""

import argparse
from contextlib import closing
import sqlite3
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from config import BASE_DIR, DATA_DIR, UPLOAD_DIR, ASSIGNMENT_DIR


def backup_sqlite_db(source_db: Path, target_db: Path) -> None:
    """Sao lưu nóng (online backup) tệp SQLite bằng API chuẩn của sqlite3."""
    with closing(sqlite3.connect(str(source_db))) as src_conn:
        with closing(sqlite3.connect(str(target_db))) as dst_conn:
            src_conn.backup(dst_conn)


def create_backup(output_dir: Path | None = None, keep: int = 10) -> Path:
    """Tạo gói sao lưu ZIP và dọn các bản sao lưu cũ vượt quá số lượng `keep`."""
    backup_root = Path(output_dir) if output_dir else (BASE_DIR / "backups")
    backup_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = backup_root / f"backup_{timestamp}.zip"
    db_path = DATA_DIR / "nopbai.db"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Sao lưu CSDL SQLite an toàn
            if db_path.exists():
                safe_db_copy = tmp_path / "nopbai.db"
                backup_sqlite_db(db_path, safe_db_copy)
                zf.write(safe_db_copy, arcname="nopbai.db")

            # 2. Sao lưu các tệp đề bài
            if ASSIGNMENT_DIR.exists():
                for file_path in ASSIGNMENT_DIR.rglob("*"):
                    if file_path.is_file():
                        rel = file_path.relative_to(DATA_DIR)
                        zf.write(file_path, arcname=rel.as_posix())

            # 3. Sao lưu các tệp bài nộp của sinh viên
            if UPLOAD_DIR.exists():
                for file_path in UPLOAD_DIR.rglob("*"):
                    if file_path.is_file():
                        rel = file_path.relative_to(DATA_DIR)
                        zf.write(file_path, arcname=rel.as_posix())

    # Dọn các bản sao lưu cũ nếu vượt quá `keep`
    if keep > 0:
        backups = sorted(
            backup_root.glob("backup_*.zip"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old_backup in backups[keep:]:
            old_backup.unlink(missing_ok=True)

    return zip_path


def main() -> None:
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Sao lưu cơ sở dữ liệu và tệp bài nộp thành gói ZIP."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BASE_DIR / "backups",
        help="Thư mục lưu bản sao lưu (mặc định: ./backups)",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=10,
        help="Số lượng bản sao lưu gần nhất cần giữ lại (0 = giữ tất cả)",
    )
    args = parser.parse_args()

    zip_path = create_backup(output_dir=args.output_dir, keep=args.keep)
    size_kb = zip_path.stat().st_size / 1024
    print(f"Đã tạo bản sao lưu thành công: {zip_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
