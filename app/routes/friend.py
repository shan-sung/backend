from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime
from uuid import uuid4
from app.models.friend_model import FriendRequestBody, FriendResponseBody, PendingFriendRequest, FriendSummary
from app.models.user_model import UserSummary

from app.auth.dependency import get_current_user
from app.database.database import get_users_collection, users_collection

router = APIRouter()

# ✅ 發送好友邀請
@router.post("/friends/request")
async def send_friend_request(
    body: FriendRequestBody,
    current_user: dict = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    to_user_id = body.to_user_id
    from_user_id = str(current_user["_id"])

    if to_user_id == from_user_id:
        raise HTTPException(status_code=400, detail="不能加自己為好友")

    target_user = await users_collection.find_one({"_id": ObjectId(to_user_id)})
    if not target_user:
        raise HTTPException(status_code=404, detail="找不到目標使用者")

    # 加入 pendingRequests 給對方
    await users_collection.update_one(
        {"_id": ObjectId(to_user_id)},
        {"$addToSet": {"pendingRequests": {
            "fromUserId": ObjectId(from_user_id),
            "timestamp": datetime.utcnow()
        }}}
    )

    await users_collection.update_one(
        {"_id": ObjectId(from_user_id)},
        {"$addToSet": {"sentRequests": ObjectId(to_user_id)}}
    )


    return {"message": "好友邀請已送出"}

# ✅ 查詢我送出的邀請
@router.get("/friends/sent", response_model=list[str])
async def get_sent_requests(
    current_user: dict = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    doc = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})
    sent = doc.get("sentRequests", [])
    return [str(uid) for uid in sent]



# ✅ 查詢我收到的邀請
@router.get("/friends/pending", response_model=list[PendingFriendRequest])
async def get_pending_requests(
    current_user: dict = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    user_doc = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})

    if not user_doc:
        raise HTTPException(status_code=404, detail="找不到使用者")

    pending_requests = user_doc.get("pendingRequests", [])

    # 取得所有 fromUserId 對應的使用者資訊
    from_user_ids = [req["fromUserId"] for req in pending_requests]
    from_users = await users_collection.find({"_id": {"$in": from_user_ids}}).to_list(length=None)
    from_user_map = {user["_id"]: user for user in from_users}  # 用 ObjectId 當 key

    enriched_requests = []
    for req in pending_requests:
        from_id = req["fromUserId"]
        user = from_user_map.get(from_id)
        if user:
            enriched_requests.append({
                "id": str(uuid4()),
                "fromUserId": str(from_id),  # ✅ 一定要轉成 str
                "toUserId": str(current_user["_id"]),
                "status": "PENDING",
                "timestamp": req["timestamp"].isoformat(),
                "fromUsername": user.get("username"),
                "fromAvatarUrl": user.get("avatarUrl", "")
            })

    return enriched_requests


# ✅ 取消送出的邀請
@router.delete("/friends/request/{to_user_id}")
async def cancel_friend_request(
    to_user_id: str,
    current_user: dict = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    from_user_id = str(current_user["_id"])

    await users_collection.update_one(
        {"_id": ObjectId(to_user_id)},
        {"$pull": {"pendingRequests": {"fromUserId": ObjectId(from_user_id)}}}
    )

    await users_collection.update_one(
        {"_id": ObjectId(from_user_id)},
        {"$pull": {"sentRequests": ObjectId(to_user_id)}}
    )

    return {"message": "好友邀請已取消"}

# ✅ 回應好友邀請（接受 / 拒絕）
@router.post("/friends/respond")
async def respond_to_friend_request(
    body: FriendResponseBody,
    current_user: dict = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    from_user_id = body.from_user_id
    to_user_id = str(current_user["_id"])

    if body.accept:
        # 雙方加進 friends
        await users_collection.update_one(
            {"_id": ObjectId(to_user_id)},
            {
                "$addToSet": {"friends": ObjectId(from_user_id)},
                "$pull": {"pendingRequests": {"fromUserId": ObjectId(from_user_id)}}
            }
        )
        await users_collection.update_one(
            {"_id": ObjectId(from_user_id)},
            {
                "$addToSet": {"friends": ObjectId(to_user_id)},
                "$pull": {"sentRequests": ObjectId(to_user_id)}
            }
        )
        return {"message": "已接受好友邀請"}
    else:
        # 拒絕 → 只是從 pending / sent 中移除
        await users_collection.update_one(
            {"_id": ObjectId(to_user_id)},
            {"$pull": {"pendingRequests": {"fromUserId": ObjectId(from_user_id)}}}
        )
        await users_collection.update_one(
            {"_id": ObjectId(from_user_id)},
            {"$pull": {"sentRequests": ObjectId(to_user_id)}}
        )
        return {"message": "已拒絕好友邀請"}


@router.get("/friends/list", response_model=list[FriendSummary])
async def get_friend_list(
    current_user: dict = Depends(get_current_user),
    users_collection: AsyncIOMotorCollection = Depends(get_users_collection)
):
    user_doc = await users_collection.find_one({"_id": current_user["_id"]})
    friend_ids = user_doc.get("friends", [])

    if not friend_ids:
        return []

    raw_friends = await users_collection.find({"_id": {"$in": friend_ids}}).to_list(length=None)

    # 使用 FriendSummary.from_mongo() 安全轉換
    summaries = []
    for f in raw_friends:
        summary = FriendSummary.from_mongo(f)
        if summary:
            summaries.append(summary)
        else:
            print(f"⚠️ 跳過不合法好友資料：{f}")

    return summaries


@router.get("/users/search", response_model=UserSummary)
async def search_user(q: str):
    user = await users_collection.find_one({"username": q})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserSummary(**user)

@router.get("/friends/validate")
async def validate_friends(
    current_user: dict = Depends(get_current_user)
):
    friend_ids = current_user.get("friends", [])
    if not friend_ids:
        return {"valid_count": 0, "invalid_ids": []}

    existing = await users_collection.find({"_id": {"$in": friend_ids}}).to_list(length=None)
    existing_ids = set(str(u["_id"]) for u in existing)
    original_ids = set(str(fid) for fid in friend_ids)
    missing = original_ids - existing_ids

    return {
        "valid_count": len(existing_ids),
        "invalid_ids": list(missing)
    }
