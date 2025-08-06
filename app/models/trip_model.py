from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.utils.py_object_id import PyObjectId
from bson import ObjectId
from app.models.schedule_model import ScheduleItem

class DaySchedule(BaseModel):
    day: int
    schedule: List[ScheduleItem]

class TravelModel(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    startDate: str
    endDate: str
    budget: int
    userId: PyObjectId
    chatRoomId: Optional[str] = None
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
