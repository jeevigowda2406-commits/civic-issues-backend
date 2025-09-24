# models/user_model.py
from db.connection import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

def create_user(email, password, name=None):
    # check if user exists
    if mongo.db.users.find_one({"email": email}):
        return None  # already exists

    hashed = generate_password_hash(password)
    user = {
        "email": email,
        "password": hashed,
        "name": name,
        "created_at": None  # optional, set if you want
    }
    res = mongo.db.users.insert_one(user)
    return str(res.inserted_id)

def find_user_by_email(email):
    u = mongo.db.users.find_one({"email": email})
    if not u:
        return None
    u["id"] = str(u["_id"])
    del u["_id"]
    # Do not return password in APIs
    u.pop("password", None)
    return u

def verify_user_credentials(email, password):
    u = mongo.db.users.find_one({"email": email})
    if not u:
        return None
    if check_password_hash(u["password"], password):
        return str(u["_id"])
    return None

def find_user_by_id(user_id):
    u = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not u:
        return None
    u["id"] = str(u["_id"])
    del u["_id"]
    u.pop("password", None)
    return u
