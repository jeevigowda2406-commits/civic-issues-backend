# routes/uploads.py
from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os
from werkzeug.utils import secure_filename

uploads_bp = Blueprint("uploads", __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload endpoint
@uploads_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, "uploads")
        os.makedirs(upload_folder, exist_ok=True)  # create folder if not exists
        file.save(os.path.join(upload_folder, filename))
        file_url = f"/uploads/{filename}"  # this is how we will serve the file
        return jsonify({"message": "File uploaded", "url": file_url}), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400

# Serve uploaded files
@uploads_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, "uploads"), filename)
