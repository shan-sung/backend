from pydantic import BaseModel
from typing import Optional

class ScheduleTime(BaseModel):
    start: str
    end: str

class ScheduleItem(BaseModel):
    day: int
    time: ScheduleTime
    placeName: str  
    transportation: str
    note: Optional[str] = ""
    placeId: Optional[str] = None
    photoReference: Optional[str] = None