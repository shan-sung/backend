from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from database import saved_collection  # 須從你的 db 模組取得 collection

router = APIRouter()

# Attraction 資料結構
class Attraction(BaseModel):
    id: str
    name: str
    category: str
    imageUrl: str = None

# 儲存一筆收藏
@router.post("/users/{user_id}/saved")
async def add_to_saved(user_id: str, attraction: Attraction):
    exists = await saved_collection.find_one({"user_id": user_id, "attraction.id": attraction.id})
    if exists:
        raise HTTPException(status_code=400, detail="Already saved.")
    await saved_collection.insert_one({
        "user_id": user_id,
        "attraction": attraction.dict()
    })
    return {"message": "Saved successfully"}

# 取得使用者收藏清單
@router.get("/users/{user_id}/saved", response_model=List[Attraction])
async def get_saved_attractions(user_id: str):
    saved = await saved_collection.find({"user_id": user_id}).to_list(length=None)
    return [item["attraction"] for item in saved]

# 移除一筆收藏
@router.delete("/users/{user_id}/saved/{attraction_id}")
async def remove_from_saved(user_id: str, attraction_id: str):
    result = await saved_collection.delete_one({"user_id": user_id, "attraction.id": attraction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attraction not found in saved list.")
    return {"message": "Removed successfully"}
