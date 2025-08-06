import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# 載入 .env 環境變數
load_dotenv()

MONGO_URI = os.getenv("MONGO_URL", "mongodb+srv://shan:13@cluster0.g54wj9s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "tripDemo-shan"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db["trips"]  # ✅ 正確的 collection 名稱

async def fix_itinerary_structure():
    trips = await collection.find().to_list(length=None)
    for trip in trips:
        updated = False
        for day in trip.get("itinerary", []):
            for item in day.get("schedule", []):
                if "place" not in item:
                    item["place"] = {
                        "source": "CUSTOM",
                        "id": item.get("placeId"),
                        "name": item.get("placeName") or "",
                        "address": None,
                        "imageUrl": item.get("photoReference"),
                        "lat": None,
                        "lng": None
                    }
                    # ✅ 清除舊欄位
                    item.pop("placeId", None)
                    item.pop("placeName", None)
                    item.pop("photoReference", None)
                    updated = True

        if updated:
            await collection.update_one(
                {"_id": trip["_id"]},
                {"$set": {"itinerary": trip["itinerary"]}}
            )
            print(f"✔ 已修正 Trip：{trip['_id']}")

    print("✅ 所有舊格式已修正完畢")

if __name__ == "__main__":
    asyncio.run(fix_itinerary_structure())
