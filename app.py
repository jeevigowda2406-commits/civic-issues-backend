# app.py
from flask import Flask
from routes.issues import issues_bp
from routes.auth import auth_bp        # << new import
from db.connection import init_db
from flask_jwt_extended import JWTManager
import os
from routes.uploads import uploads_bp



API_KEY = "SIH2025SECRET"

def create_app():
    app = Flask(__name__)
    # MongoDB URI config
    app.config["MONGO_URI"] = "mongodb://localhost:27017/civic_issues_db"
    # JWT secret (keep this secret in production; put in .env)
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "THERESOLVERS")

    init_db(app)  # initialize mongo
    jwt = JWTManager(app)

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    init_db(app)  # initialize mongo
    app.register_blueprint(issues_bp, url_prefix="/api")  # register routes
    app.register_blueprint(uploads_bp, url_prefix="/api")  # register uploads routes
    # Add the home route here inside create_app
    @app.route("/")
    def home():
        return "Welcome to the Civic Issues API! Use /api/issues to see issues."

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
