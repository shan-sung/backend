from pydantic import BaseModel
from bson import ObjectId
from typing import Optional
from pydantic import Field
from app.utils.py_object_id import PyObjectId

# models/friend_model.py
class FriendRequestBody(BaseModel):
    from_user_id: str
    to_user_id: str

class FriendResponseBody(BaseModel):
    from_user_id: str
    accept: bool

class PendingFriendRequest(BaseModel):
    id: str  # 如果這是 _id 就設 alias="_id"
    fromUserId: str
    toUserId: str
    status: str
    timestamp: str
    fromUsername: str
    fromAvatarUrl: str


class FriendSummary(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    avatarUrl: Optional[str] = None
    mbti: Optional[str] = "N/A"
    email: Optional[str] = "N/A"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

    @staticmethod
    def from_mongo(doc: dict) -> Optional["FriendSummary"]:
        try:
            if not doc.get("_id") or not doc.get("username"):
                return None
            # 設定預設值
            doc.setdefault("mbti", "N/A")
            doc.setdefault("email", "N/A")
            doc.setdefault("avatarUrl", None)
            return FriendSummary(**doc)
        except Exception as e:
            print(f"❌ FriendSummary parsing error: {e} for doc {doc}")
            return None