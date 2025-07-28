# utils/py_object_id.py
from bson import ObjectId
from pydantic import BaseModel
from pydantic.json import ENCODERS_BY_TYPE

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

# 讓 Pydantic 知道如何編碼 ObjectId
ENCODERS_BY_TYPE[ObjectId] = str
