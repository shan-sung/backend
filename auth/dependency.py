# get_current_user.py
from fastapi import Request, HTTPException
from jose import jwt, JWTError
from bson import ObjectId
from pymongo import MongoClient
import os
from auth.auth_utils import SECRET_KEY, ALGORITHM

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
users_collection = client["tripdb"]["users"]

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header[len("Bearer "):]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")