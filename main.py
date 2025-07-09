from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

app = FastAPI()

# 跨域設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發用 "*"，正式環境請改成指定網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return [serialize_doc(t) for t in trips]

@app.post("/trips")
def create_generated_trip(trip: dict = Body(...)):
    trip["createdAt"] = datetime.utcnow()
    result = trips_collection.insert_one(trip)
    trip["_id"] = str(result.inserted_id)
    return trip