from pydantic import BaseModel, Field
from app.utils.py_object_id import PyObjectId
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

class UserSummary(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    email: Optional[str] = "N/A"
    mbti: Optional[str] = "N/A"
    birthday: Optional[datetime]
    bio: Optional[str]
    avatarUrl: Optional[str]
    phoneNumber: Optional[str]
    friends: List[PyObjectId] = []

    model_config = {
        "populate_by_name": True,
        "json_encoders": {
            ObjectId: str,
            datetime: lambda d: d.isoformat()
        }
    }