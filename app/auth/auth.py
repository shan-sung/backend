# app/auth/auth.py
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from app.auth.utils import verify_password, create_access_token, convert_mongo_user
from app.database import users_collection
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest = Body(...)):
    user = await users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": str(user["_id"])})
    return {
        "user": convert_mongo_user(user),
        "token": token
    }
