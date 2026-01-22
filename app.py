from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
import os
import io
from database import init_db


def create_app():
    app = Flask(__name__, static_folder="frontend", static_url_path="")
    app.config.from_object("config.Config")

    init_db(app)
    CORS(app)  # Разрешить CORS для фронтенда

    # Импорт всех blueprints
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.requests import requests_bp
    from routes.comments import comments_bp
    from routes.stat import statistics_bp

    # Регистрация blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(statistics_bp)

    # QR-код для формы обратной связи
    @app.get("/qr/feedback")
    def qr_feedback():
        import qrcode  # pip install qrcode[pil]
        url = app.config.get("FEEDBACK_FORM_URL")

        if not url:
            return {"error": "FEEDBACK_FORM_URL is not set"}, 500

        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return send_file(buf, mimetype="image/png")

    # Главная страница (фронтенд)
    @app.route("/")
    @app.route("/index.html")
    def index():
        return send_from_directory("frontend", "index.html")

    # Catch-all для SPA (раздача фронтенда)
    @app.route("/<path:path>")
    def catch_all(path):
        # Если запрос к API — вернуть 404
        if path.startswith("api/"):
            return {"error": "Not found"}, 404

        # Проверить, существует ли файл
        full_path = os.path.join("frontend", path)
        if os.path.exists(full_path):
            return send_from_directory("frontend", path)

        # Иначе вернуть index.html (для SPA маршрутизации)
        return send_from_directory("frontend", "index.html")

    return app


if __name__ == "__main__":
    app = create_app()

    print("\n" + "=" * 70)
    print("🚀 Сервер запущен на http://192.168.0.21:5000")
    print("📊 Доступные эндпоинты:")
    print("   - POST /api/auth/login")
    print("   - GET  /api/users/")
    print("   - GET  /api/requests/")
    print("   - GET  /api/comments/")
    print("   - GET  /api/statistics/")
    print("   - GET  /qr/feedback")
    print("=" * 70 + "\n")

    app.run(host="192.168.0.21", port=5000, debug=True)
