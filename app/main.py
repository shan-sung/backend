from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

from app.auth.auth import router as auth_router
from app.routes.friend import router as friend_router
from app.routes.trip_request import router as trip_request_router
from app.routes.trip import router as trip_router
from app.routes.schedule import router as schedule_router
from app.routes.chatroom import router as chatroom_router
from app.routes.saved import router as saved_router
load_dotenv()

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(friend_router)
app.include_router(trip_request_router)
app.include_router(trip_router)
app.include_router(schedule_router)
app.include_router(chatroom_router)
app.include_router(saved_router)
