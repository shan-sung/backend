from fastapi import APIRouter, Body, HTTPException, Path
from app.models.chat_model import ChatMessageModel
from app.database.database import chat_messages_collection

router = APIRouter()

@router.get("/chatrooms/{trip_id}/messages", response_model=list[ChatMessageModel])
async def get_chat_messages(trip_id: str = Path(...)):
    messages = await chat_messages_collection.find({"chatRoomId": trip_id}).sort("timestamp", 1).to_list(length=None)
    return messages

@router.post("/chatrooms/{trip_id}/messages", response_model=ChatMessageModel)
async def post_chat_message(trip_id: str, message: ChatMessageModel = Body(...)):
    msg_dict = message.dict(by_alias=True)
    msg_dict["chatRoomId"] = trip_id  # ✅ 安全一致
    await chat_messages_collection.insert_one(msg_dict)
    return msg_dict