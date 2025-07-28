from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class FriendRequestBody(BaseModel):
    _id: Optional[str]  # 如果你要回傳 MongoDB 的 _id
    from_user_id: str
    to_user_id: str

    class Config:
        json_encoders = {
            ObjectId: str
        }

class FriendResponseBody(BaseModel):
    from_user_id: str
    accept: bool

class PendingFriendRequest(BaseModel):
    id: str
    fromUserId: str
    toUserId: str
    status: str
    timestamp: str
    fromUsername: str
    fromAvatarUrl: str

class AddMembersRequest(BaseModel):
    memberIds: list[str]