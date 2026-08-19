# =========================================================
# SAFE CAMPUS - DATABASE CONFIGURATION
# =========================================================

import os

from pymongo import MongoClient


# =========================================================
# MONGODB SETTINGS
# =========================================================

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

DATABASE_NAME = os.environ.get("DATABASE_NAME", "safe_campus")


# =========================================================
# DATABASE CONNECTION
# =========================================================

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client[DATABASE_NAME]


# =========================================================
# COLLECTIONS
# =========================================================

users_collection = db["users"]

alerts_collection = db["sos_alerts"]

history_collection = db["emergency_history"]


# =========================================================
# DATABASE CONNECTION CHECK
# =========================================================

def check_database_connection():
    """
    Check whether MongoDB is reachable.
    """

    try:

        client.admin.command("ping")

        return True

    except Exception as error:

        print(
            "MongoDB Connection Error:",
            error
        )

        return False