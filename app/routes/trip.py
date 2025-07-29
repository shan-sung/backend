# app/routes/trip.py
from fastapi import APIRouter, Depends, HTTPException, Body
from bson import ObjectId
from datetime import datetime
from uuid import uuid4
from app.models.trip_model import TravelModel, AddMembersRequest
from app.database.database import trips_collection, chat_messages_collection
from app.auth.dependency import get_current_user
from app.utils.date import calculate_days

AI_ASSISTANT_ID = ObjectId("68873646be69d9f12e537d8f")

router = APIRouter()

@router.get("/trips", response_model=list[TravelModel])
async def get_all_generated_trips():
    trips = await trips_collection.find().to_list(length=None)
    for trip in trips:
        trip["days"] = calculate_days(trip.get("startDate", ""), trip.get("endDate", ""))
    return trips


@router.get("/trips/{trip_id}", response_model=TravelModel)
async def get_trip_by_id(trip_id: str):
    trip = await trips_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip["days"] = calculate_days(trip.get("startDate", ""), trip.get("endDate", ""))
    return trip


@router.post("/trips", response_model=TravelModel)
async def create_generated_trip(trip: TravelModel = Body(...), user=Depends(get_current_user)):
    trip_dict = trip.dict(by_alias=True)

    # 產生 Trip 資料
    trip_dict["_id"] = ObjectId()
    trip_dict["userId"] = ObjectId(user["_id"])
    trip_dict["chatRoomId"] = str(uuid4())
    trip_dict["createdAt"] = datetime.utcnow()

    # 處理成員列表（包含主揪自己）
    members = [ObjectId(user["_id"])] + [ObjectId(uid) for uid in trip_dict.get("members", [])]
    trip_dict["members"] = members

    # 插入 Trip
    await trips_collection.insert_one(trip_dict)

    return trip_dict


@router.delete("/trips/{trip_id}")
async def delete_trip(trip_id: str, user=Depends(get_current_user)):
    # ✅ 先找出 trip 資料
    trip = await trips_collection.find_one({"_id": ObjectId(trip_id), "userId": ObjectId(user["_id"])})

    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or unauthorized")

    # ✅ 先刪聊天室訊息
    await chat_messages_collection.delete_many({"chatRoomId": trip["chatRoomId"]})

    # ✅ 再刪 Trip
    await trips_collection.delete_one({"_id": ObjectId(trip_id)})

    return {"message": "Trip and chatroom deleted"}


@router.post("/trips/{trip_id}/members")
async def add_members_to_trip(trip_id: str, request: AddMembersRequest, user=Depends(get_current_user)):
    trip = await trips_collection.find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    if str(trip["userId"]) != str(user["_id"]):
        raise HTTPException(status_code=403, detail="Only the trip owner can invite members")

    existing_members = set(str(uid) for uid in trip.get("members", []))
    incoming_members = set(request.memberIds)
    new_member_ids = list(incoming_members - existing_members)

    if not new_member_ids:
        return {"message": "No new members to add."}

    object_ids = [ObjectId(uid) for uid in new_member_ids]

    await trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$addToSet": {"members": {"$each": object_ids}}}
    )

    return {"message": "New members added successfully", "added": new_member_ids}



@router.get("/my-trips", response_model=list[TravelModel])
async def get_user_trips(user=Depends(get_current_user)):
    trips = await trips_collection.find({"userId": ObjectId(user["_id"])}).to_list(length=None)
    return trips