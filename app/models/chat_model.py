from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatMessage(BaseModel):
    id: str
    chatRoomId: str
    senderId: str
    sender: str
    message: str
    timestamp: int  # milliseconds
