# routes/issues.py
from flask import Blueprint, request, jsonify
from models.issue_model import create_issue, get_all_issues, get_issue_by_id, update_issue, delete_issue
from db.connection import mongo
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

issues_bp = Blueprint("issues_bp", __name__)


# Upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# POST - create new issue
# POST - create new issue
@issues_bp.route("/issues", methods=["POST"])
@jwt_required()
def add_issue():
    user = get_jwt_identity()
    title = request.form.get("title")
    description = request.form.get("description")
    location = request.form.get("location")
    image = request.files.get("image")
    
    # Optional GPS
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    image_filename = None
    if image:
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, image_filename))

    # Convert latitude/longitude to float if provided
    lat = float(latitude) if latitude else None
    lng = float(longitude) if longitude else None

    issue_data = {
        "title": title,
        "description": description,
        "location": location,
        "image": image_filename,
        "status": "pending",        # default status
        "created_by": user,
        "latitude": lat,
        "longitude": lng
    }

    issue_id = create_issue(issue_data)
    return jsonify({"message": "Issue created", "id": str(issue_id)}), 201

# GET - list all issues (public)
@issues_bp.route("/issues", methods=["GET"])
def list_issues():
    filters = {}
    status = request.args.get("status")
    location = request.args.get("location")
    title = request.args.get("title")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc")

    if status:
        filters["status"] = status
    if location:
        filters["location"] = location
    if title:
        filters["title"] = title

    result = get_all_issues(filters, page, limit, sort, order)
    return jsonify(result), 200


# GET - get single issue by id (public)
@issues_bp.route("/issues/<issue_id>", methods=["GET"])
def get_issue(issue_id):
    issue = get_issue_by_id(issue_id)
    if issue:
        return jsonify(issue), 200
    return jsonify({"error": "Issue not found"}), 404


# PUT - update an issue
@issues_bp.route("/issues/<issue_id>", methods=["PUT"])
@jwt_required()
def update(issue_id):
    data = request.json
    user = get_jwt_identity()
    data["updated_by"] = user
    success = update_issue(issue_id, data)
    if success:
        return jsonify({"message": "Issue updated"}), 200
    return jsonify({"error": "Issue not found"}), 404


# DELETE - delete an issue
@issues_bp.route("/issues/<issue_id>", methods=["DELETE"])
@jwt_required()
def delete(issue_id):
    user = get_jwt_identity()
    success = delete_issue(issue_id, user)
    if success:
        return jsonify({"message": "Issue deleted"}), 200
    return jsonify({"error": "Issue not found"}), 404


# GET - stats of issues by status
@issues_bp.route("/issues/stats", methods=["GET"])
def issues_stats():
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    stats = list(mongo.db.issues.aggregate(pipeline))
    result = {item["_id"]: item["count"] for item in stats}
    return jsonify(result), 200

# PATCH - update only status of an issue
@issues_bp.route("/issues/<issue_id>/status", methods=["PATCH"])
@jwt_required()
def update_status(issue_id):
    data = request.json
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error": "Status is required"}), 400

    user = get_jwt_identity()
    success = update_issue(issue_id, {"status": new_status, "updated_by": user})
    if success:
        return jsonify({"message": f"Issue status updated to '{new_status}'"}), 200
    return jsonify({"error": "Issue not found"}), 404


