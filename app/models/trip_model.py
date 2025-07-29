# models/trip_model.py
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.utils.py_object_id import PyObjectId
from bson import ObjectId
from app.models.schedule_model import ScheduleTime

class ScheduleEntry(BaseModel):
    time: ScheduleTime
    placeName: str  # ✅ 必填欄位
    transportation: str
    note: Optional[str] = ""
    placeId: Optional[str] = None
    photoReference: Optional[str] = None

class DaySchedule(BaseModel):
    day: int
    schedule: List[ScheduleEntry]

class TravelModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    startDate: str
    endDate: str
    budget: int
    userId: PyObjectId
    chatRoomId: Optional[str] = None   # ✅ 新增：關聯聊天室
    members: Optional[List[PyObjectId]] = []
    itinerary: Optional[List[DaySchedule]] = []
    imageUrl: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TripRequestInput(BaseModel):
    title: str
    startDate: str
    endDate: str
    budget: int


class AddMembersRequest(BaseModel):
    memberIds: list[str]