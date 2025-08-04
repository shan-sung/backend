from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.utils.py_object_id import PyObjectId

class Comment(BaseModel):
    user: str
    rating: int
    text: str

class Attraction(BaseModel):
    id: str
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None
    userRatingsTotal: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    imageUrl: Optional[str] = None
    address: Optional[str] = None
    openingHours: Optional[List[str]] = None