from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from app.utils.auth import require_auth

upload_bp = Blueprint("upload", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "avi", "mov", "mkv"}


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@upload_bp.route("/images", methods=["POST"])
@require_auth
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({"error": "File type not allowed for images"}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "uploads", "images"
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    return jsonify(
        {
            "message": "Image uploaded successfully",
            "filename": unique_filename,
            "url": f"/uploads/images/{unique_filename}",
        }
    ), 201


@upload_bp.route("/videos", methods=["POST"])
@require_auth
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
        return jsonify({"error": "File type not allowed for videos"}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "uploads", "videos"
    )
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    return jsonify(
        {
            "message": "Video uploaded successfully",
            "filename": unique_filename,
            "url": f"/uploads/videos/{unique_filename}",
        }
    ), 201
