from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from auth.auth_utils import verify_password, create_access_token, convert_mongo_user
from pymongo import MongoClient
from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from auth.auth_utils import SECRET_KEY, ALGORITHM
from pymongo import MongoClient
from bson import ObjectId
import os

router = APIRouter(prefix="/auth", tags=["auth"])

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
users_collection = client["tripdb"]["users"]

class LoginRequest(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    email: str

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


@router.post("/login")
def login(request: LoginRequest = Body(...)):
    user = users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": str(user["_id"])})
    return {
        "user": convert_mongo_user(user),  # ✅ 回傳轉換後格式
        "token": token
    }