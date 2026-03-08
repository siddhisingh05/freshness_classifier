from flask import Flask
from .models.database import init_db
from .routes.auth import bcrypt
import os


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-prod")
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    app.config["DATABASE"] = os.environ.get("DATABASE_URL", "freshness.db")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    bcrypt.init_app(app)

    with app.app_context():
        init_db()

    from .routes.main import main_bp
    from .routes.predict import predict_bp
    from .routes.history import history_bp
    from .routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(auth_bp)

    return app
