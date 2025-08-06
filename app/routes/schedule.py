from fastapi import APIRouter, Body, HTTPException
from bson import ObjectId
from app.models.schedule_model import ScheduleItem
from app.database.database import trips_collection

router = APIRouter()

def build_schedule_entry(item: ScheduleItem) -> dict:
    return {
        "time": {"start": item.time.start, "end": item.time.end},
        "transportation": item.transportation,
        "note": item.note or "",
        "place": item.place.dict()
    }

@router.post("/trips/{travel_id}/schedule")
async def add_schedule_item(travel_id: str, item: ScheduleItem = Body(...)):
    if not ObjectId.is_valid(travel_id):
        raise HTTPException(status_code=400, detail="Invalid travel_id")

    travel = await trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    itinerary = travel.get("itinerary", [])

    # 建立 entry
    entry = build_schedule_entry(item)

    # 加入對應 day
    for day_entry in itinerary:
        if day_entry.get("day") == item.day:
            day_entry["schedule"].append(entry)
            break
    else:
        itinerary.append({"day": item.day, "schedule": [entry]})

    # 排序 day（確保一致性）
    itinerary.sort(key=lambda d: d["day"])

    await trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": itinerary}}
    )
    return {"message": "Schedule item added successfully"}

@router.put("/trips/{travel_id}/schedule/{original_day}/{index}")
async def update_schedule_item(
    travel_id: str,
    original_day: int,
    index: int,
    item: ScheduleItem = Body(...)
):
    if not ObjectId.is_valid(travel_id):
        raise HTTPException(status_code=400, detail="Invalid travel_id")

    travel = await trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    itinerary = travel.get("itinerary", [])

    # Step 1: Remove from original day
    original_day_entry = next((d for d in itinerary if d.get("day") == original_day), None)
    if original_day_entry:
        if 0 <= index < len(original_day_entry["schedule"]):
            original_day_entry["schedule"].pop(index)
            if not original_day_entry["schedule"]:
                itinerary.remove(original_day_entry)
        else:
            raise HTTPException(status_code=400, detail="Index out of range for original_day")
    else:
        raise HTTPException(status_code=400, detail="Original day not found")

    # Step 2: Add to new day
    target_day_entry = next((d for d in itinerary if d.get("day") == item.day), None)
    if not target_day_entry:
        target_day_entry = {"day": item.day, "schedule": []}
        itinerary.append(target_day_entry)

    target_day_entry["schedule"].append(build_schedule_entry(item))

    # Step 3: Sort itinerary
    itinerary.sort(key=lambda d: d["day"])

    await trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": itinerary}}
    )
    return {"message": "Schedule item updated successfully"}

@router.delete("/trips/{travel_id}/schedule/{day}/{index}")
async def delete_schedule_item(travel_id: str, day: int, index: int):
    travel = await trips_collection.find_one({"_id": ObjectId(travel_id)})
    if not travel:
        raise HTTPException(status_code=404, detail="Trip not found")

    if "itinerary" not in travel or not isinstance(travel["itinerary"], list):
        raise HTTPException(status_code=400, detail="Invalid itinerary data")

    # 找到對應 day
    day_entry = next((d for d in travel["itinerary"] if d.get("day") == day), None)
    if not day_entry or index >= len(day_entry["schedule"]):
        raise HTTPException(status_code=404, detail="Schedule item not found")

    # 移除該 index
    day_entry["schedule"].pop(index)

    # 如果 schedule 清空了，移除整天
    if not day_entry["schedule"]:
        travel["itinerary"].remove(day_entry)

    await trips_collection.update_one(
        {"_id": ObjectId(travel_id)},
        {"$set": {"itinerary": travel["itinerary"]}}
    )

    return {"message": "Schedule item deleted successfully"}
