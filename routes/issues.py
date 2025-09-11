# routes/issues.py
from flask import Blueprint, request, jsonify
from models.issue_model import create_issue, get_all_issues, get_issue_by_id, update_issue, delete_issue, add_comment, get_comments, delete_comment
from functools import wraps  
from db.connection import mongo
from werkzeug.utils import secure_filename
import os
from bson.objectid import ObjectId


issues_bp = Blueprint("issues", __name__)

# ✅ Decorator to require API key
API_KEY = "SIH2025SECRET"

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get("x-api-key") != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# POST - create new issue
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@issues_bp.route("/issues", methods=["POST"])
@require_api_key
def add_issue():
    title = request.form.get("title")
    description = request.form.get("description")
    location = request.form.get("location")
    image = request.files.get("image")  # this gets the uploaded file

    # optionally save image
    image_filename = None
    if image:
        image_filename = secure_filename(image.filename)
        image.save(f"./uploads/{image_filename}")  # save locally

    issue_id = create_issue({
        "title": title,
        "description": description,
        "location": location,
        "image": image_filename
    })
    return jsonify({"message": "Issue created", "id": str(issue_id)}), 201


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
@require_api_key
def update(issue_id):
    data = request.json
    success = update_issue(issue_id, data)
    if success:
        return jsonify({"message": "Issue updated"}), 200
    return jsonify({"error": "Issue not found"}), 404

# DELETE - delete an issue
@issues_bp.route("/issues/<issue_id>", methods=["DELETE"])
@require_api_key
def delete(issue_id):
    success = delete_issue(issue_id)
    if success:
        return jsonify({"message": "Issue deleted"}), 200
    return jsonify({"error": "Issue not found"}), 404


@issues_bp.route("/issues/stats", methods=["GET"])
def issues_stats():
    # Aggregation pipeline: count issues by status
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    stats = list(mongo.db.issues.aggregate(pipeline))
    result = {item["_id"]: item["count"] for item in stats}
    return jsonify(result), 200

# POST comment to an issue
@issues_bp.route("/issues/<issue_id>/comments", methods=["POST"])
@require_api_key
def add_issue_comment(issue_id):
    data = request.json
    comment = data.get("comment")
    author = data.get("author")
    comment_id = add_comment(issue_id, comment, author)
    return jsonify({"message": "Comment added", "id": comment_id}), 201

# GET all comments for an issue
@issues_bp.route("/issues/<issue_id>/comments", methods=["GET"])
def list_issue_comments(issue_id):
    comments = get_comments(issue_id)
    return jsonify(comments), 200

#Delete comment by an id
@issues_bp.route("/issues/<issue_id>/comments/<comment_id>", methods=["DELETE"])
@require_api_key
def remove_issue_comment(issue_id, comment_id):
    from models.issue_model import delete_comment
    success = delete_comment(issue_id, comment_id)
    if success:
        return jsonify({"message": "Comment deleted"}), 200
    return jsonify({"error": "Comment not found"}), 404

