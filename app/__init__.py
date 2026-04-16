from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from sqlalchemy import text
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

    from .routes.user_routes import user_bp
    from .routes.upload_routes import upload_bp

    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(upload_bp, url_prefix="/upload")

    return app