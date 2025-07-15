from fastapi import Request, HTTPException
from jose import jwt, JWTError
from bson import ObjectId
import os
from app.auth.utils import SECRET_KEY, ALGORITHM
from app.database.database import users_collection

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth_header[len("Bearer "):]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")
