import os

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime


# =========================================================
# MONGODB CONNECTION
# =========================================================

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "safe_campus")

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

users = db["users"]
sos_alerts = db["sos_alerts"]
emergency_history = db["emergency_history"]


# =========================================================
# USERS
# =========================================================

def register_user(name, email, phone, password, role):
    """
    Register a new user.
    Compatible with the existing register.py.
    """

    email = email.strip().lower()

    # Check duplicate email
    if users.find_one({"email": email}):
        return False

    users.insert_one({
        "name": name,
        "email": email,
        "phone": phone,
        "password": password,
        "role": role,
        "created_at": datetime.now()
    })

    return True


def login_user(email, password):
    """
    Login existing user.
    Compatible with the existing login.py.
    """

    email = email.strip().lower()

    return users.find_one({
        "email": email,
        "password": password
    })


def get_user_by_email(email):
    """
    Find user by email.
    """

    email = email.strip().lower()

    return users.find_one({
        "email": email
    })


def get_user_by_id(user_id):
    """
    Find user by MongoDB ObjectId.
    """

    try:
        return users.find_one({
            "_id": ObjectId(user_id)
        })
    except Exception:
        return None


def get_all_users():
    """
    Get all users.
    """

    return list(
        users.find().sort("created_at", -1)
    )


def delete_user(user_id):
    """
    Delete a user.
    """

    try:

        result = users.delete_one({
            "_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    except Exception as error:

        print("Delete User Error:", error)

        return False


# =========================================================
# SOS ALERTS
# =========================================================

def create_sos(
    student_id,
    student_name,
    latitude,
    longitude
):
    """
    Create a new SOS alert.
    """

    try:

        alert = {
            "student_id": ObjectId(student_id),
            "student_name": student_name,
            "latitude": latitude,
            "longitude": longitude,
            "status": "Pending",
            "created_at": datetime.now()
        }

        result = sos_alerts.insert_one(alert)

        return result.inserted_id

    except Exception as error:

        print("Create SOS Error:", error)

        return None


def get_all_alerts():
    """
    Get all SOS alerts.
    Newest first.
    """

    return list(
        sos_alerts.find().sort("created_at", -1)
    )


def get_active_alerts():
    """
    Get pending SOS alerts.
    """

    return list(
        sos_alerts.find({
            "status": "Pending"
        }).sort("created_at", -1)
    )


def update_alert_status(alert_id, status):
    """
    Update SOS alert status.
    """

    try:

        result = sos_alerts.update_one(
            {
                "_id": ObjectId(alert_id)
            },
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.now()
                }
            }
        )

        return result.modified_count > 0

    except Exception as error:

        print("Update Alert Error:", error)

        return False


def delete_alert(alert_id):
    """
    Delete SOS alert.
    """

    try:

        result = sos_alerts.delete_one({
            "_id": ObjectId(alert_id)
        })

        return result.deleted_count > 0

    except Exception as error:

        print("Delete Alert Error:", error)

        return False


# =========================================================
# EMERGENCY HISTORY
# =========================================================

def save_history(
    alert_id,
    student_name,
    security_name,
    latitude,
    longitude,
    remarks
):
    """
    Save resolved emergency into history.
    """

    try:

        history = {
            "alert_id": ObjectId(alert_id),
            "student_name": student_name,
            "security_name": security_name,
            "latitude": latitude,
            "longitude": longitude,
            "resolved_at": datetime.now(),
            "remarks": remarks
        }

        result = emergency_history.insert_one(history)

        return result.inserted_id

    except Exception as error:

        print("Save History Error:", error)

        return None


def get_history():
    """
    Get emergency history.
    Newest first.
    """

    return list(
        emergency_history.find().sort(
            "resolved_at",
            -1
        )
    )


# =========================================================
# DEFAULT ADMIN
# =========================================================

def create_default_admin():
    """
    Create default Admin if one does not exist.
    """

    admin = users.find_one({
        "role": "Admin"
    })

    if admin is None:

        users.insert_one({

            "name": "Administrator",

            "email": "admin@gmail.com",

            "password": "admin123",

            "phone": "03000000000",

            "role": "Admin",

            "created_at": datetime.now()
        })

        print("Default Admin Created.")


# =========================================================
# DATABASE STARTUP
# =========================================================

create_default_admin()

print(
    "Safe Campus Database Connected Successfully!"
)