import os
import sys

from waitress import serve

from app import create_app

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

app = create_app()


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    threads = int(os.environ.get("WAITRESS_THREADS", 8))

    if os.environ.get("FLASK_DEBUG", "0") == "1":
        app.run(host=host, port=port, debug=True)
    else:
        print(f"Đang chạy máy chủ Waitress tại http://{host}:{port} (threads={threads})")
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            max_request_body_size=app.config["MAX_CONTENT_LENGTH"],
        )
