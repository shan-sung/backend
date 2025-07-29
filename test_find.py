import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def test_find():
    client = AsyncIOMotorClient("mongodb+srv://shan:13@cluster0.g54wj9s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # 換成你的 Mongo URI
    db = client["tripDemo-shan"]
    col = db["saved_attractions"]
    result = await col.find({"user_id": ObjectId("6881df76be69d9f12e537d3d")}).to_list(length=None)
    print("找到幾筆：", len(result))

asyncio.run(test_find())
