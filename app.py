# app.py
from flask import Flask
from routes.issues import issues_bp
from db.connection import init_db, mongo

def create_app():
    app = Flask(__name__)
    # MongoDB URI config
    app.config["MONGO_URI"] = "mongodb://localhost:27017/civic_issues_db"
    init_db(app)  # initialize mongo
    app.register_blueprint(issues_bp, url_prefix="/api")  # register routes

    @app.route("/")
    def home():
        return "Welcome to the Civic Issues API! Use /api/issues to see issues."

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

API_KEY = "SIH2025SECRET"
