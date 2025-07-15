from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = "tripDemo-shan"

client = AsyncIOMotorClient(MONGO_URL)
db = client[db_name]

users_collection = db["users"]
trips_collection = db["trips"]
saved_collection = db["saved_attractions"]
requests_collection = db["trip_requests"]