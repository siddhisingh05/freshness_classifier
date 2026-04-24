from flask import Flask
from .models.database import init_db
from .routes.auth import bcrypt
import os



def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get("SECRET_KEY") or "dev-secret-key"
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    app.config["DATABASE"] = os.environ.get("DATABASE_URL", "freshness.db")


    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    bcrypt.init_app(app)

    with app.app_context():
        init_db()

    register_blueprints(app)
    return app


def register_blueprints(app):
    from .routes.main import main_bp
    from .routes.predict import predict_bp
    from .routes.history import history_bp
    from .routes.auth import auth_bp

    for bp in (main_bp, predict_bp, history_bp, auth_bp):
        app.register_blueprint(bp)
