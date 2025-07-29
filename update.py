# Python 修復程式（建議執行一次性腳本）
from pymongo import MongoClient

client = MongoClient("mongodb+srv://shan:13@cluster0.g54wj9s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["tripDemo-shan"]
collection = db["trips"]

trips = collection.find()
for trip in trips:
    modified = False
    for day in trip.get("itinerary", []):
        for item in day.get("schedule", []):
            if "placeName" not in item and "activity" in item:
                item["placeName"] = item.pop("activity")
                modified = True
    if modified:
        collection.replace_one({"_id": trip["_id"]}, trip)
