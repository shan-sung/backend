import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://shan:13@cluster0.g54wj9s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

client = AsyncIOMotorClient(MONGO_URL)
db = client["tripDemo-shan"]

async def insert_sample_data():
    # --------- 1. trips ----------
    trips_doc = {
        "_id": ObjectId("686c1f0b08af08fbca1c01df"),
        "userId": ObjectId("6872987ee46f8990c73180a1"),
        "title": "環島冒險",
        "startDate": "2025-07-07",
        "endDate": "2025-07-16",
        "members": ["user1", "user2", "user3"],
        "budget": 20000,
        "description": "探索東台灣與南部海岸線，體驗自然與文化。",
        "imageUrl": "https://example.com/image1.jpg",
        "createdAt": datetime.fromisoformat("2025-07-07T19:24:59.596000"),
        "itinerary": [
            {
                "day": 1,
                "schedule": [
                    {
                        "time": {"start": "09:00", "end": "10:30"},
                        "activity": "故宮博物院",
                        "transportation": "捷運",
                        "note": "可提前10分鐘抵達"
                    },
                    {
                        "time": {"start": "11:00", "end": "13:00"},
                        "activity": "鼎泰豐",
                        "transportation": "捷運",
                        "note": "記得領錢"
                    },
                    {
                        "time": {"start": "13:00", "end": "15:00"},
                        "activity": "台北101",
                        "transportation": "步行"
                    },
                    {
                        "time": {"start": "15:30", "end": "18:00"},
                        "activity": "xx民宿",
                        "transportation": "計程車",
                        "note": "Check-in ＋ 桌遊"
                    },
                    {
                        "time": {"start": "18:00", "end": "21:00"},
                        "activity": "饒河夜市",
                        "transportation": "公車",
                        "note": "輸的請客"
                    },
                    {
                        "time": {"start": "00:00", "end": "01:00"},
                        "activity": "Riverside",
                        "transportation": "MRT"
                    },
                    {
                        "time": {"start": "04:00", "end": "06:00"},
                        "activity": "Place",
                        "transportation": "Walk",
                        "note": "note"
                    }
                ]
            },
            {
                "day": 2,
                "schedule": [
                    {
                        "time": {"start": "09:30", "end": "11:00"},
                        "activity": "陽明山竹子湖",
                        "transportation": "公車",
                        "note": "穿好走的鞋，賞花拍照"
                    },
                    {
                        "time": {"start": "11:30", "end": "13:00"},
                        "activity": "草山夜未眠 午餐",
                        "transportation": "計程車",
                        "note": "景觀餐廳"
                    },
                    {
                        "time": {"start": "13:30", "end": "15:30"},
                        "activity": "北投溫泉博物館",
                        "transportation": "公車",
                        "note": "可泡腳或拍照"
                    },
                    {
                        "time": {"start": "16:00", "end": "17:30"},
                        "activity": "誠品生活",
                        "transportation": "捷運",
                        "note": "文青逛街＋下午茶"
                    },
                    {
                        "time": {"start": "18:00", "end": "21:00"},
                        "activity": "士林夜市",
                        "transportation": "步行",
                        "note": "炸雞排、青蛙下蛋不能錯過"
                    }
                ]
            },
            {
                "day": 3,
                "schedule": [
                    {
                        "time": {"start": "09:00", "end": "10:30"},
                        "activity": "中正紀念堂",
                        "transportation": "捷運",
                        "note": "看升旗、衛兵交接"
                    },
                    {
                        "time": {"start": "11:00", "end": "13:00"},
                        "activity": "永康街美食",
                        "transportation": "步行",
                        "note": "牛肉麵、冰品可選"
                    },
                    {
                        "time": {"start": "13:30", "end": "15:00"},
                        "activity": "華山文創園區",
                        "transportation": "捷運",
                        "note": "有展覽、文創小店"
                    },
                    {
                        "time": {"start": "15:30", "end": "17:30"},
                        "activity": "光點台北",
                        "transportation": "步行",
                        "note": "老建築＋咖啡"
                    },
                    {
                        "time": {"start": "18:00", "end": "20:30"},
                        "activity": "寧夏夜市",
                        "transportation": "公車",
                        "note": "豆花、蚵仔煎推薦"
                    }
                ]
            },
            {"day": 4, "schedule": []},
            {"day": 5, "schedule": []},
            {"day": 6, "schedule": [
                {
                    "time": {"start": "09:00", "end": "09:00"},
                    "activity": "test",
                    "transportation": "test",
                    "note": "test"
                }
            ]},
            {"day": 7, "schedule": []},
            {"day": 8, "schedule": []},
            {"day": 9, "schedule": []},
            {"day": 10, "schedule": []},
        ]
    }

    await db["trips"].insert_one(trips_doc)

    # --------- 2. trip_requests ----------
    trip_request_doc = {
        "_id": ObjectId("686c93b65c07811e1ad9f3dc"),
        "averageAgeRange": "18–24",
        "budget": 10000,
        "cities": ["台南市"],
        "endDate": {},
        "peopleCount": 1,
        "preferences": ["Adventure"],
        "startDate": {},
        "title": "Trip 0708-1",
        "transportOptions": ["Walking"],
        "createdAt": datetime.fromisoformat("2025-07-08T03:42:46.635000")
    }

    await db["trip_requests"].insert_one(trip_request_doc)

    # --------- 3. users ----------
    user_doc = {
        "_id": ObjectId("6872987ee46f8990c73180a1"),
        "username": "johndoe",
        "email": "johndoe@example.com",
        "password": "$2b$12$5NTMyR5itjzzM9g2wq3AcejEH10JzMSzlHs0n7Fyb9hHYNgIONXNa",
        "mbti": "INTJ",
        "birthday": "2000-05-15",
        "phoneNumber": "+886912345678",
        "bio": "喜歡旅行與攝影的工程師"
    }

    await db["users"].insert_one(user_doc)

    # --------- 4. saved_attractions ----------
    saved_doc = {
        "_id": ObjectId("6874a02976cd44f76b1cacd2"),
        "user_id": "6872987ee46f8990c73180a1",
        "attraction": {
            "id": "ChIJVVqEhB1QbzQR13uNBi976Gc",
            "name": "Kiwit 奇美 AMIS 奇美部落",
            "category": "Art Museum",
            "imageUrl": "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=ATKogpcNB96VY462JPosoh7GHSWoaQHoWJ4WHf9MxHV91vLBfADOzrD8vniFMFr7oWEyGA64Qmk_NNhlPt8OJhb6sufwQS_sTRv_NLvvZuzGdbP31wzu6ocwr8nlSveIIlxXTynHwuAWwSfYSlw6S1_VoOSp7iCQN2pZbRT3eiENJXi2DTTpobVy3U1FUKt-DZ4Dsd4Dw4bo1E84sFaKcqYGCBcqMSq12TJXhkJTOtL1fqlSqrVYYMEXxcGU7P24RTvyMyGGaut0uaiaCG5ME9SqbrShLgkvjo_0wB280TkSqvsv-XtvBd74bf_NE-cPL5I4FkEKh4yqmVM&key=AIzaSyC0D-Po3aRGYtx4nZPiik3HjhTKmnIHrGU"
        }
    }

    await db["saved_attractions"].insert_one(saved_doc)

    print("✅ 所有資料成功插入")

if __name__ == "__main__":
    asyncio.run(insert_sample_data())
