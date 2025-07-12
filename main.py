from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from auth.auth import router as auth_router
from auth.dependency import get_current_user
from routes import saved

load_dotenv()

app = FastAPI()
app.include_router(auth_router)
app.include_router(saved.router)


# 加入 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScheduleTime(BaseModel):
    start: str
    end: str

class ScheduleItem(BaseModel):
    day: int
    time: ScheduleTime
    activity: str
    transportation: str
    note: str = ""

# MongoDB 設定
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["tripdb"]
requests_collection = db["trip_requests"]
trips_collection = db["trips"]

# ObjectId 序列化工具
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# -----------------------
# Trip Request API
# -----------------------

def calculate_days(start_date: str, end_date: str) -> int:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days + 1
    except Exception:
        return 0  # 如果格式錯誤則回傳 0 或丟出例外視情況

@app.post("/trip-requests")
def create_trip_request(trip_request: dict = Body(...)):
    trip_request["createdAt"] = datetime.utcnow()
    result = requests_collection.insert_one(trip_request)
    trip_request["_id"] = str(result.inserted_id)
    return trip_request

@app.get("/trip-requests")
def get_all_trip_requests():
    requests = list(requests_collection.find())
    return [serialize_doc(r) for r in requests]

# -----------------------
# Generated Trips API
# -----------------------

@app.get("/trips")
def get_all_generated_trips():
    trips = list(trips_collection.find())
    for trip in trips:
        trip["days"] = calculate_days(trip.get("startDate", ""), trip.get("endDate", ""))
    return [serialize_doc(t) for t in trips]

@app.post("/trips")
def create_generated_trip(trip: dict = Body(...), user=Depends(get_current_user)):
    try:
        trip["userId"] = ObjectId(user["_id"])  # ✅ 綁定登入者
        trip["createdAt"] = datetime.utcnow()

        result = trips_collection.insert_one(trip)
        trip["_id"] = str(result.inserted_id)

        print(f"✅ Inserted trip with ID: {result.inserted_id}")
        return trip
    except Exception as e:
        print(f"❌ Failed to insert trip: {e}")
        raise HTTPException(status_code=500, detail="Insert failed")

@app.post("/trips/{travel_id}/schedule")
def add_schedule_item(travel_id: str, item: ScheduleItem = Body(...)):
    travel = trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    if "itinerary" not in travel:
        travel["itinerary"] = []

    schedule_entry = {
        "time": {
            "start": item.time.start,
            "end": item.time.end
        },
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

    trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": travel["itinerary"]}}
    )

    return {"message": "Schedule item added successfully"}

@app.get("/my-trips")
def get_user_trips(user=Depends(get_current_user)):
    trips = trips_collection.find({"userId": ObjectId(user["_id"])})
    return [serialize_doc(t) for t in trips]