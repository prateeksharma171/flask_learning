from flask import Flask, send_from_directory
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy import text
from .routes.auth_routes import auth_bp
from .routes.upload_routes import upload_bp
from .db import db
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            logger.info("✅ DB Connected!")
        except Exception as e:
            logger.error("❌ DB Connection Failed!")
            logger.exception(e)
            return app

        try:
            from app.models.user import User

            db.create_all()
            logger.info("✅ Tables created successfully!")
        except Exception as e:
            logger.error("❌ Table creation failed!")
            logger.exception(e)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(upload_bp, url_prefix="/upload")

    uploads_folder = os.path.join(os.path.dirname(__file__), "uploads")

    @app.route("/uploads/images/<path:filename>")
    def serve_image(filename):
        return send_from_directory(os.path.join(uploads_folder, "images"), filename)

    @app.route("/uploads/videos/<path:filename>")
    def serve_video(filename):
        return send_from_directory(os.path.join(uploads_folder, "videos"), filename)

    return app
