from pymongo import MongoClient
import os
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# 2. Fetch the URI. 
# If MONGO_URI isn't found (e.g. in production), it falls back to localhost
MONGO_DETAILS = os.getenv("MONGO_URI", "mongodb://localhost:27017") 

# Connect using standard Pymongo client
client = MongoClient(MONGO_DETAILS, serverSelectionTimeoutMS=5000)

# Database Name
db = client.fastapi_analytics

# Collections
blog_collection = db["blogs"]

# Helper: Fix MongoDB _id serialization
def blog_helper(blog) -> dict:
    return {
        "id": str(blog["_id"]),
        "title": blog["title"],
        "content": blog["content"],
        "author": blog["author"],
        "date": blog["date"],
    }