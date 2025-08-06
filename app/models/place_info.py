from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SourceType(str, Enum):
    google = "GOOGLE"
    custom = "CUSTOM"


class PlaceInfo(BaseModel):
    source: SourceType
    id: Optional[str] = None
    name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    imageUrl: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    userRatingsTotal: Optional[int] = None  # ✅ 加這行！
    openingHours: Optional[list[str]] = None 