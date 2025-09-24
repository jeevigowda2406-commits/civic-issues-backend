# db/connection.py
from flask_pymongo import PyMongo

mongo = PyMongo()  # global mongo instance

def init_db(app):
    """Initialize PyMongo with the Flask app"""
    mongo.init_app(app)
    return mongo
