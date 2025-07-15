from pydantic import BaseModel

class ScheduleTime(BaseModel):
    start: str
    end: str

class ScheduleItem(BaseModel):
    day: int
    time: ScheduleTime
    activity: str
    transportation: str
    note: str = ""
