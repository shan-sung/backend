# models/chat_model.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.utils.py_object_id import PyObjectId
from bson import ObjectId

class ChatMessageModel(BaseModel):
    chatRoomId: Optional[str] = None
    senderId: PyObjectId
    sender: str
    message: str
    timestamp: datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
