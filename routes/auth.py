# routes/auth.py
from flask import Blueprint, request, jsonify
from models.user_model import create_user, verify_user_credentials, find_user_by_id
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    try:
        user_id = create_user(email, password, name)
        if not user_id:
            return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        print("Error creating user:", e)
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"message": "User created", "id": str(user_id)}), 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user_id = verify_user_credentials(email, password)
    if not user_id:
        return jsonify({"error": "Invalid credentials"}), 401

    # create JWT access token; identity = user_id
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token}), 200
