from pydantic import BaseModel
from typing import Optional
from app.models.place_info import PlaceInfo

class ScheduleTime(BaseModel):
    start: str  # e.g., "08:00"
    end: str    # e.g., "09:00"

class ScheduleItem(BaseModel):
    day: int  # ✅ 補上這行
    time: ScheduleTime
    transportation: str
    note: Optional[str] = None
    place: PlaceInfo
