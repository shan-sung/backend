from fastapi import FastAPI, Body, Depends, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os
import logging

from app.auth.auth import router as auth_router
from app.auth.dependency import get_current_user
from app.routes import saved, user, friend
from app.database.database import requests_collection, trips_collection, chat_messages_collection
from app.models.schedule_model import ScheduleItem
from app.models.chat_model import ChatMessage
from app.models.friend_model import AddMembersRequest

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(auth_router)
app.include_router(saved.router)
app.include_router(user.router)
app.include_router(friend.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def serialize_doc(doc):
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    elif isinstance(doc, dict):
        return {
            k: serialize_doc(v)
            for k, v in doc.items()
        }
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc


def calculate_days(start_date: str, end_date: str) -> int:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days + 1
    except Exception:
        return 0

# -----------------------
# Trip Request API
# -----------------------
@app.post("/trip-requests")
async def create_trip_request(trip_request: dict = Body(...)):
    from uuid import uuid4

    trip_request["createdAt"] = datetime.utcnow()

    await requests_collection.insert_one(trip_request)

    fake_travel = {
        "_id": str(uuid4()),
        "title": trip_request.get("title", "Untitled Trip"),
        "startDate": trip_request.get("startDate"),
        "endDate": trip_request.get("endDate"),
        "budget": trip_request.get("budget"),
        "members": [],
        "itinerary": [
            {
                "day": 1,
                "schedule": [
                    {
                        "time": {"start": "09:00", "end": "10:00"},
                        "activity": "Breakfast",
                        "transportation": "Walk",
                        "note": "Local cafe"
                    }
                ]
            }
        ],
        "imageUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
    }

    return fake_travel


@app.get("/trip-requests")
async def get_all_trip_requests():
    requests = await requests_collection.find().to_list(length=None)
    return [serialize_doc(r) for r in requests]

# -----------------------
# Trips API
# -----------------------
@app.get("/trips")
async def get_all_generated_trips():
    trips = await trips_collection.find().to_list(length=None)
    for trip in trips:
        trip["days"] = calculate_days(trip.get("startDate", ""), trip.get("endDate", ""))
    return serialize_doc(trips)  # ✅ 對整個 list 套用 serialize_doc

@app.get("/trips/{trip_id}")
async def get_trip_by_id(trip_id: str):
    trip = await trips_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip["days"] = calculate_days(trip.get("startDate", ""), trip.get("endDate", ""))
    return serialize_doc(trip)

@app.post("/trips")
async def create_generated_trip(trip: dict = Body(...), user=Depends(get_current_user)):
    try:
        trip["userId"] = ObjectId(user["_id"])
        trip["createdAt"] = datetime.utcnow()
        result = await trips_collection.insert_one(trip)
        trip["_id"] = str(result.inserted_id)
        return serialize_doc(trip)
    except Exception as e:
        logger.error(f"❌ Failed to insert trip: {e}")
        raise HTTPException(status_code=500, detail="Insert failed")

@app.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str, user=Depends(get_current_user)):
    result = await trips_collection.delete_one({"_id": ObjectId(trip_id), "userId": ObjectId(user["_id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized")
    return {"message": "Trip deleted"}

@app.post("/trips/{trip_id}/members")
async def add_members_to_trip(
    trip_id: str,
    request: AddMembersRequest,
    user=Depends(get_current_user)
):
    trip = await trips_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if str(trip["userId"]) != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Only the trip owner can invite members")

    # 避免重複，使用 $addToSet + $each
    await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {
            "$addToSet": {
                "members": {
                    "$each": [ObjectId(uid) for uid in request.memberIds]
                }
            }
        }
    )

    return {"message": "Members added successfully"}
# -----------------------
# Schedule API
# -----------------------
@app.post("/trips/{travel_id}/schedule")
async def add_schedule_item(travel_id: str, item: ScheduleItem = Body(...)):
    travel = await trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    if "itinerary" not in travel:
        travel["itinerary"] = []

    schedule_entry = {
        "time": {"start": item.time.start, "end": item.time.end},
        "activity": item.activity,
        "transportation": item.transportation,
        "note": item.note
    }

    for day in travel["itinerary"]:
        if day["day"] == item.day:
            day["schedule"].append(schedule_entry)
            break
    else:
        travel["itinerary"].append({"day": item.day, "schedule": [schedule_entry]})

    await trips_collection.update_one({"_id": ObjectId(travel_id)}, {"$set": {"itinerary": travel["itinerary"]}})
    return {"message": "Schedule item added successfully"}

@app.put("/trips/{travel_id}/schedule/{day}/{index}")
async def update_schedule_item(travel_id: str, day: int, index: int, item: ScheduleItem = Body(...)):
    travel = await trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    if "itinerary" not in travel or not isinstance(travel["itinerary"], list):
        travel["itinerary"] = []

    matched_day = next((d for d in travel["itinerary"] if d.get("day") == day), None)
    if matched_day is None:
        matched_day = {"day": day, "schedule": []}
        travel["itinerary"].append(matched_day)

    travel["itinerary"].sort(key=lambda d: d["day"])

    while len(matched_day["schedule"]) <= index:
        matched_day["schedule"].append({"time": {"start": "", "end": ""}, "activity": "", "transportation": "", "note": ""})

    matched_day["schedule"][index] = {
        "time": {"start": item.time.start, "end": item.time.end},
        "activity": item.activity,
        "transportation": item.transportation,
        "note": item.note or ""
    }

    await trips_collection.update_one({"_id": ObjectId(travel_id)}, {"$set": {"itinerary": travel["itinerary"]}})
    return {"message": "Schedule item updated successfully"}

# -----------------------
# User's Trips API
# -----------------------
@app.get("/my-trips")
async def get_user_trips(user=Depends(get_current_user)):
    trips = await trips_collection.find({"userId": ObjectId(user["_id"])}).to_list(length=None)
    return [serialize_doc(t) for t in trips]

# -----------------------
# Chatroom API
# -----------------------
@app.get("/chatrooms/{trip_id}/messages")
async def get_chat_messages(trip_id: str = Path(...)):
    messages = await chat_messages_collection.find({"chatRoomId": trip_id}).sort("timestamp", 1).to_list(length=None)
    return [serialize_doc(msg) for msg in messages]

@app.post("/chatrooms/{trip_id}/messages")
async def post_chat_message(trip_id: str, message: ChatMessage = Body(...)):
    msg_dict = message.dict()
    msg_dict["chatRoomId"] = trip_id
    await chat_messages_collection.insert_one(msg_dict)
    return {"status": "success", "message": "Message sent"}