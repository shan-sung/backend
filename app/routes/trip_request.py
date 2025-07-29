from fastapi import APIRouter
from datetime import datetime
from uuid import uuid4
from app.database.database import requests_collection
from app.models.trip_model import TripRequestInput

router = APIRouter()

@router.post("/trip-requests")
async def create_trip_request(trip_request: TripRequestInput):
    trip_request_dict = trip_request.dict()
    trip_request_dict["createdAt"] = datetime.utcnow()
    await requests_collection.insert_one(trip_request_dict)

    fake_travel = {
        "_id": str(uuid4()),
        "title": trip_request_dict.get("title", "Untitled Trip"),
        "startDate": trip_request_dict.get("startDate"),
        "endDate": trip_request_dict.get("endDate"),
        "budget": trip_request_dict.get("budget"),
        "members": [],
        "itinerary": [{
            "day": 1,
            "schedule": [{
                "time": {"start": "09:00", "end": "10:00"},
                "activity": "Breakfast",
                "transportation": "Walk",
                "note": "Local cafe"
            }]
        }],
        "imageUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
    }
    return fake_travel

@router.get("/trip-requests")
async def get_all_trip_requests():
    return await requests_collection.find().to_list(length=None)
