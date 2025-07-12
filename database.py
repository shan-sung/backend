from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["tripdb"]
saved_collection = db["saved_attractions"]

