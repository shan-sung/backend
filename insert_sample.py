from pymongo import MongoClient
from datetime import datetime

# MongoDB 連線設定
client = MongoClient("mongodb://localhost:27017")
db = client["tripdb"]
requests_collection = db["trip_requests"]
trips_collection = db["trips"]

# 插入 Trip Requests（使用者輸入）
trip_requests = [
    {
        "title": "環島冒險",
        "startDate": "2025-08-01",
        "endDate": "2025-08-10",
        "peopleCount": 3,
        "averageAgeRange": "21-25",
        "preferences": ["自然景觀", "美食"],
        "transportOptions": ["火車", "租車"],
        "cities": ["花蓮", "台東", "墾丁"],
        "budget": 20000,
        "createdAt": datetime.utcnow()
    },
    {
        "title": "北部城市小旅行",
        "startDate": "2025-07-15",
        "endDate": "2025-07-17",
        "peopleCount": 2,
        "averageAgeRange": "26-30",
        "preferences": ["購物", "夜市"],
        "transportOptions": ["大眾運輸"],
        "cities": ["台北", "新北"],
        "budget": 6000,
        "createdAt": datetime.utcnow()
    },
    {
        "title": "花東慢活之旅",
        "startDate": "2025-09-01",
        "endDate": "2025-09-05",
        "peopleCount": 1,
        "averageAgeRange": "31-35",
        "preferences": ["放鬆", "自然景觀"],
        "transportOptions": ["火車"],
        "cities": ["花蓮", "台東"],
        "budget": 8000,
        "createdAt": datetime.utcnow()
    },
    {
        "title": "親子樂園假期",
        "startDate": "2025-08-15",
        "endDate": "2025-08-18",
        "peopleCount": 4,
        "averageAgeRange": "6-40",
        "preferences": ["親子活動", "遊樂園"],
        "transportOptions": ["開車"],
        "cities": ["台中", "南投"],
        "budget": 15000,
        "createdAt": datetime.utcnow()
    },
    {
        "title": "南部文化深度遊",
        "startDate": "2025-10-01",
        "endDate": "2025-10-07",
        "peopleCount": 2,
        "averageAgeRange": "36-45",
        "preferences": ["歷史", "文化", "在地美食"],
        "transportOptions": ["高鐵", "捷運"],
        "cities": ["台南", "高雄", "屏東"],
        "budget": 18000,
        "createdAt": datetime.utcnow()
    }
]

requests_collection.insert_many(trip_requests)
print("✅ Inserted 5 trip_requests")

# 插入 Generated Trips（AI 行程建議）
generated_trips = [
    {
        "title": "環島冒險",
        "created": True,
        "days": 10,
        "members": 3,
        "budget": 20000,
        "description": "探索東台灣與南部海岸線，體驗自然與文化。",
        "imageUrl": "https://example.com/image1.jpg",
        "createdAt": datetime.utcnow()
    },
    {
        "title": "北部城市小旅行",
        "created": True,
        "days": 3,
        "members": 2,
        "budget": 6000,
        "description": "都市快閃與夜市美食探索行程。",
        "imageUrl": "https://example.com/image2.jpg",
        "createdAt": datetime.utcnow()
    },
    {
        "title": "花東慢活之旅",
        "created": True,
        "days": 5,
        "members": 1,
        "budget": 8000,
        "description": "遠離塵囂，走進花東的山海靜謐。",
        "imageUrl": "https://example.com/image3.jpg",
        "createdAt": datetime.utcnow()
    },
    {
        "title": "親子樂園假期",
        "created": True,
        "days": 4,
        "members": 4,
        "budget": 15000,
        "description": "以親子互動與遊樂設施為主的放鬆行程。",
        "imageUrl": "https://example.com/image4.jpg",
        "createdAt": datetime.utcnow()
    },
    {
        "title": "南部文化深度遊",
        "created": True,
        "days": 7,
        "members": 2,
        "budget": 18000,
        "description": "探訪南台灣的古蹟與在地風味餐廳。",
        "imageUrl": "https://example.com/image5.jpg",
        "createdAt": datetime.utcnow()
    }
]

trips_collection.insert_many(generated_trips)
print("✅ Inserted 5 generated trips")
