from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://shan:13@cluster0.g54wj9s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_name = "tripDemo-shan"

client = AsyncIOMotorClient(MONGO_URL)
db = client[db_name]

users_collection = db["users"]
trips_collection = db["trips"]
saved_collection = db["saved_attractions"]
requests_collection = db["trip_requests"]
chat_messages_collection = db["chat_messages"]