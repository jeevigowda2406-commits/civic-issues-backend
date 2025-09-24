from db.connection import mongo
from bson.objectid import ObjectId
from datetime import datetime

def create_issue(data):
    now = datetime.utcnow()
    issue = {
        "title": data.get("title"),
        "description": data.get("description"),
        "location": data.get("location"),
        "status": data.get("status", "pending"),
        "image": data.get("image"), 
        "created_by": data.get("created_by"),
        "latitude": data.get("latitude"),   # optional
        "longitude": data.get("longitude"), # optional
        "created_at": now,
        "updated_at": now
    }
    return mongo.db.issues.insert_one(issue).inserted_id



def get_all_issues(filters=None, page=1, limit=10, sort="created_at", order="desc"):
    query = {}

    if filters:
        if "status" in filters:
            query["status"] = filters["status"]
        if "location" in filters:
            query["location"] = {"$regex": filters["location"], "$options": "i"}
        if "title" in filters:
            query["title"] = {"$regex": filters["title"], "$options": "i"}

    # Sorting
    sort_order = -1 if order == "desc" else 1
    total_count = mongo.db.issues.count_documents(query)
    total_pages = (total_count + limit - 1) // limit  # ceil division

    # Pagination + sort
    cursor = (
        mongo.db.issues.find(query)
        .sort(sort, sort_order)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    issues = []
    for issue in cursor:
        issue["id"] = str(issue["_id"])
        del issue["_id"]
        issues.append(issue)

    return {
        "issues": issues,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "total_count": total_count,
    }


def get_issue_by_id(issue_id):
    issue = mongo.db.issues.find_one({"_id": ObjectId(issue_id)})
    if issue:
        issue["id"] = str(issue["_id"])
        del issue["_id"]
    return issue


def update_issue(issue_id, data):
    data["updated_at"] = datetime.utcnow()
    result = mongo.db.issues.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": data}
    )
    return result.modified_count > 0


def delete_issue(issue_id, user=None):
    """
    If user is provided, only delete if user is the creator.
    """
    query = {"_id": ObjectId(issue_id)}
    if user:
        query["created_by"] = user

    result = mongo.db.issues.delete_one(query)
    return result.deleted_count > 0
