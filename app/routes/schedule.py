from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from app.models.schedule_model import ScheduleItem
from app.database.database import trips_collection

router = APIRouter()

@router.post("/trips/{travel_id}/schedule")
async def add_schedule_item(travel_id: str, item: ScheduleItem = Body(...)):
    travel = await trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    if "itinerary" not in travel:
        travel["itinerary"] = []

    # ✅ 將所有欄位都包含進 schedule_entry
    schedule_entry = {
        "time": {"start": item.time.start, "end": item.time.end},
        "transportation": item.transportation,
        "note": item.note,
        "placeId": item.placeId,
        "placeName": item.placeName,
        "photoReference": item.photoReference
    }

    # ✅ 放進對應的 day
    for day in travel["itinerary"]:
        if day["day"] == item.day:
            day["schedule"].append(schedule_entry)
            break
    else:
        travel["itinerary"].append({"day": item.day, "schedule": [schedule_entry]})

    await trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": travel["itinerary"]}}
    )
    return {"message": "Schedule item added successfully"}

@router.put("/trips/{travel_id}/schedule/{day}/{index}")
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
        matched_day["schedule"].append({
            "time": {"start": "", "end": ""},
            "transportation": "",
            "note": "",
            "placeId": None,
            "placeName": None,
            "photoReference": None
        })

    # ✅ 將所有欄位一併更新
    matched_day["schedule"][index] = {
        "time": {"start": item.time.start, "end": item.time.end},
        "placeName": item.placeName,
        "transportation": item.transportation,
        "note": item.note or "",
        "placeId": item.placeId,
        "photoReference": item.photoReference
    }

    await trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": travel["itinerary"]}}
    )
    return {"message": "Schedule item updated successfully"}