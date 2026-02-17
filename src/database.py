from motor.motor_asyncio import AsyncIOMotorClient

from config import DB_NAME, MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
admins_collection = db["admins"]
required_channels_collection = db["required_channels"]
