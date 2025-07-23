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
from app.models.friend_model import FriendRequestBody

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
    return {
        k: str(v) if isinstance(v, ObjectId) else v
        for k, v in doc.items()
    }


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
    trip_request["createdAt"] = datetime.utcnow()
    result = await requests_collection.insert_one(trip_request)
    trip_request["_id"] = str(result.inserted_id)
    return trip_request

@app.get("/trip-requests")
async def get_all_trip_requests():
    requests = await requests_collection.find().to_list(length=None)
    return [serialize_doc(r) for r in requests]

# -----------------------
# Generated Trips API
# -----------------------

@app.get("/trips")
async def get_all_generated_trips():
    trips = await trips_collection.find().to_list(length=None)
    for trip in trips:
        trip["days"] = calculate_days(trip.get("startDate", ""), trip.get("endDate", ""))
    return [serialize_doc(t) for t in trips]

@app.post("/trips")
async def create_generated_trip(trip: dict = Body(...), user=Depends(get_current_user)):
    try:
        trip["userId"] = ObjectId(user["_id"])
        trip["createdAt"] = datetime.utcnow()
        result = await trips_collection.insert_one(trip)
        trip["_id"] = str(result.inserted_id)
        logger.info(f"✅ Inserted trip with ID: {result.inserted_id}")
        return trip
    except Exception as e:
        logger.error(f"❌ Failed to insert trip: {e}")
        raise HTTPException(status_code=500, detail="Insert failed")

@app.get("/trips/{trip_id}")
async def get_trip_by_id(trip_id: str):
    trip = await trips_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    trip["days"] = calculate_days(trip.get("startDate", ""), trip.get("endDate", ""))
    return serialize_doc(trip)


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

    updated = False
    for day in travel["itinerary"]:
        if day["day"] == item.day:
            day["schedule"].append(schedule_entry)
            updated = True
            break

    if not updated:
        travel["itinerary"].append({
            "day": item.day,
            "schedule": [schedule_entry]
        })

    await trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": travel["itinerary"]}}
    )

    return {"message": "Schedule item added successfully"}


@app.put("/trips/{travel_id}/schedule/{day}/{index}")
async def update_schedule_item(
    travel_id: str,
    day: int = Path(..., description="第幾天"),
    index: int = Path(..., description="當天 schedule 的 index"),
    item: ScheduleItem = Body(...)
):
    travel = await trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    # 確保 itinerary 存在
    if "itinerary" not in travel or not isinstance(travel["itinerary"], list):
        travel["itinerary"] = []

    # ✅ 建立或取得指定 day 的行程
    matched_day = next((d for d in travel["itinerary"] if d.get("day") == day), None)
    if matched_day is None:
        matched_day = {
            "day": day,
            "schedule": []
        }
        travel["itinerary"].append(matched_day)

    # ✅ 確保 itinerary 排序正確（避免 index 對不上）
    travel["itinerary"].sort(key=lambda d: d["day"])

    # ✅ 自動補 schedule[] 至 index 長度
    while len(matched_day["schedule"]) <= index:
        matched_day["schedule"].append({
            "time": {"start": "", "end": ""},
            "activity": "",
            "transportation": "",
            "note": ""
        })

    # ✅ 安全更新目標項目
    matched_day["schedule"][index] = {
        "time": {"start": item.time.start, "end": item.time.end},
        "activity": item.activity,
        "transportation": item.transportation,
        "note": item.note or ""
    }

    # ✅ 儲存整個 itinerary
    await trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": travel["itinerary"]}}
    )

    return {"message": "Schedule item updated successfully"}


@app.get("/my-trips")
async def get_user_trips(user=Depends(get_current_user)):
    trips = await trips_collection.find({"userId": ObjectId(user["_id"])}).to_list(length=None)
    return [serialize_doc(t) for t in trips]

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