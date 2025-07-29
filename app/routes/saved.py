from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from app.database.database import saved_collection
from app.models.attraction_model import Attraction

router = APIRouter()

# 工具函式：驗證並轉換 ObjectId
def validate_object_id(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    return ObjectId(id_str)

# 儲存一筆收藏
@router.post("/users/{user_id}/saved")
async def add_to_saved(user_id: str, attraction: Attraction):
    user_obj_id = validate_object_id(user_id)
    exists = await saved_collection.find_one({
        "user_id": user_obj_id,
        "attraction.id": attraction.id
    })
    if exists:
        raise HTTPException(status_code=400, detail="Already saved.")
    await saved_collection.insert_one({
        "user_id": user_obj_id,
        "attraction": attraction.dict()
    })
    return {"message": "Saved successfully"}

# 取得使用者收藏清單
@router.get("/users/{user_id}/saved", response_model=List[Attraction])
async def get_saved_attractions(user_id: str):
    user_obj_id = validate_object_id(user_id)
    saved = await saved_collection.find({"user_id": user_obj_id}).to_list(length=None)
    print(f"🧪 找到 {len(saved)} 筆收藏")
    return [item["attraction"] for item in saved]


# 移除一筆收藏
@router.delete("/users/{user_id}/saved/{attraction_id}")
async def remove_from_saved(user_id: str, attraction_id: str):
    user_obj_id = validate_object_id(user_id)
    result = await saved_collection.delete_one({
        "user_id": user_obj_id,
        "attraction.id": attraction_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attraction not found in saved list.")
    return {"message": "Removed successfully"}