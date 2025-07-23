from pydantic import BaseModel

class FriendRequestBody(BaseModel):
    to_user_id: str

class FriendResponseBody(BaseModel):
    from_user_id: str
    accept: bool
