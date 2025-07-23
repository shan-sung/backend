from fastapi import APIRouter, HTTPException, Query
from app.database.database import users_collection

router = APIRouter()

@router.get("/users/search")
async def search_user(q: str):
    user = await users_collection.find_one({"username": q})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user.get("email"),
        "mbti": user.get("mbti", "N/A"),
        "birthday": user.get("birthday"),  # 如果是 datetime，要轉成字串
        "bio": user.get("bio"),
        "avatarUrl": user.get("avatarUrl"),
        "phoneNumber": user.get("phoneNumber"),
        "friends": user.get("friends", [])
    }