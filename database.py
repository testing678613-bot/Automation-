from datetime import datetime, timezone, timedelta
from typing import Optional

from src.database import admins_collection, required_channels_collection, users_collection


async def get_user(user_id: int) -> dict:
    return await users_collection.find_one({"user_id": user_id}) or {"user_id": user_id}


async def upsert_user(user_id: int, **fields):
    await users_collection.update_one({"user_id": user_id}, {"$set": fields}, upsert=True)


async def set_language(user_id: int, language: str):
    await upsert_user(user_id, language=language)


async def set_payment_type(user_id: int, payment_type: str):
    await upsert_user(user_id, payment_type=payment_type)


async def activate_plan(user_id: int, days: int, added_by: int, payment_type: Optional[str] = None):
    expiry = datetime.now(timezone.utc) + timedelta(days=days)
    fields = {"plan_expiry": expiry, "added_by": added_by}
    if payment_type:
        fields["payment_type"] = payment_type
    await upsert_user(user_id, **fields)
    return expiry


async def extend_plan(user_id: int, days: int):
    user = await get_user(user_id)
    now = datetime.now(timezone.utc)
    current = user.get("plan_expiry")
    if current and current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    base = current if current and current > now else now
    expiry = base + timedelta(days=days)
    await upsert_user(user_id, plan_expiry=expiry)
    return expiry


async def remove_plan(user_id: int):
    await users_collection.update_one({"user_id": user_id}, {"$unset": {"plan_expiry": "", "payment_type": "", "added_by": ""}})


async def get_plan_expiry(user_id: int):
    user = await get_user(user_id)
    expiry = user.get("plan_expiry")
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return expiry


async def has_active_plan(user_id: int) -> bool:
    expiry = await get_plan_expiry(user_id)
    return bool(expiry and expiry > datetime.now(timezone.utc))


async def get_expired_users(now: datetime):
    return users_collection.find({"plan_expiry": {"$lte": now}})


async def is_admin(user_id: int, fallback_admin_ids: list[int]) -> bool:
    if user_id in fallback_admin_ids:
        return True
    return await admins_collection.find_one({"user_id": user_id}) is not None


async def add_admin(user_id: int):
    await admins_collection.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)


async def remove_admin(user_id: int):
    await admins_collection.delete_one({"user_id": user_id})


async def set_required_channels(channels: list[str]):
    await required_channels_collection.update_one({"key": "required"}, {"$set": {"channels": channels}}, upsert=True)


async def get_required_channels(default: list[str]) -> list[str]:
    doc = await required_channels_collection.find_one({"key": "required"})
    if doc and doc.get("channels"):
        return doc["channels"]
    return default
