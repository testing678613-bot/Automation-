import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, List
from src import database as db

autoreply_collection = db.db["autoreply_settings"]
autoreply_log_collection = db.db["autoreply_log"]
banned_words_collection = db.db["banned_words"]

DEFAULT_COOLDOWN_MINUTES = 1
DEFAULT_OFFLINE_COOLDOWN_MINUTES = 1
MAX_BANNED_WORDS = 50
BANNED_DELETE_RATE_LIMIT = 20
BANNED_DELETE_WINDOW = 60
BANNED_DELETE_PAUSE = 10

DEFAULT_OFFLINE_TEXT = """🎉 𝗧𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝗖𝗼𝗻𝘁𝗮𝗰𝘁𝗶𝗻𝗴 𝗨𝘀

🗓 We're c𝘂𝗿𝗿𝗲𝗻𝘁𝗹𝘆 𝗢𝗳𝗳𝗹𝗶𝗻𝗲 𝗱𝘂𝗲 𝘁𝗼 𝘂𝗻𝗸𝗻𝗼𝘄𝗻 𝗿𝗲𝗮𝘀𝗼𝗻𝘀.

✅ 𝗣𝗹𝗲𝗮𝘀𝗲 𝗯𝗲 𝗽𝗮𝗶𝘁𝗲𝗻𝘁 𝗮𝗻𝗱 𝗦𝗲𝗻𝗱 𝘂𝘀 𝘆𝗼𝘂𝗿 𝗾𝗮𝘂𝗲𝗿𝗶𝗲𝘀 ❗️"""

offline_log_collection = db.db["offline_log"]

_delete_timestamps = defaultdict(list)
_delete_paused_until = {}

AUTO_REPLY_MARKERS = [
    "auto-reply", "auto reply", "autoreply", "automated response",
    "i am currently unavailable", "i'm currently unavailable",
    "this is an automated", "auto response"
]


async def get_autoreply_settings(user_id: int) -> dict:
    settings = await autoreply_collection.find_one({"user_id": user_id})
    if not settings:
        settings = {
            "user_id": user_id,
            "enabled": False,
            "template_text": "",
            "photo_file_id": None,
            "cooldown_minutes": DEFAULT_COOLDOWN_MINUTES,
        }
    return settings


async def set_template_text(user_id: int, text: str):
    await autoreply_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "template_text": text,
            "last_updated": datetime.utcnow()
        }},
        upsert=True
    )


async def set_photo_file_id(user_id: int, file_id: str):
    await autoreply_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "photo_file_id": file_id,
            "last_updated": datetime.utcnow()
        }},
        upsert=True
    )


async def clear_photo(user_id: int):
    await autoreply_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "photo_file_id": None,
            "last_updated": datetime.utcnow()
        }},
        upsert=True
    )


async def toggle_autoreply(user_id: int, enabled: bool):
    await autoreply_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "enabled": enabled,
            "last_updated": datetime.utcnow()
        }},
        upsert=True
    )


async def can_reply_now(user_id: int, peer_id: int) -> bool:
    settings = await get_autoreply_settings(user_id)
    cooldown_minutes = settings.get("cooldown_minutes", DEFAULT_COOLDOWN_MINUTES)

    log_entry = await autoreply_log_collection.find_one({
        "user_id": user_id,
        "peer_id": peer_id
    })

    if log_entry:
        last_replied = log_entry.get("last_replied")
        if last_replied:
            cutoff = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
            if last_replied > cutoff:
                return False

    return True


async def mark_replied(user_id: int, peer_id: int):
    await autoreply_log_collection.update_one(
        {"user_id": user_id, "peer_id": peer_id},
        {"$set": {
            "last_replied": datetime.utcnow()
        }},
        upsert=True
    )


def render_template(template_text: str, first_name: str = "", username: str = "", chat_id: int = 0) -> str:
    now = datetime.utcnow()
    rendered = template_text.replace("{first_name}", first_name or "")
    rendered = rendered.replace("{username}", f"@{username}" if username else "")
    rendered = rendered.replace("{chat_id}", str(chat_id))
    rendered = rendered.replace("{date}", now.strftime("%d/%m/%Y"))
    rendered = rendered.replace("{time}", now.strftime("%I:%M %p"))
    return rendered


def is_auto_reply_loop(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    for marker in AUTO_REPLY_MARKERS:
        if marker in lower:
            return True
    return False


async def get_banned_words(user_id: int) -> List[str]:
    doc = await banned_words_collection.find_one({"user_id": user_id})
    if doc:
        return doc.get("words", [])
    return []


async def add_banned_word(user_id: int, word: str) -> tuple:
    word = word.strip()
    if not word or len(word) > 50:
        return False, "Word must be 1-50 characters."
    word_lower = word.lower()
    existing = await get_banned_words(user_id)
    for w in existing:
        if w.lower() == word_lower:
            return False, "Word already exists."
    if len(existing) >= MAX_BANNED_WORDS:
        return False, f"Maximum {MAX_BANNED_WORDS} words allowed."
    await banned_words_collection.update_one(
        {"user_id": user_id},
        {"$push": {"words": word}, "$set": {"updated_at": datetime.utcnow()}},
        upsert=True
    )
    return True, "Word added."


async def remove_banned_word(user_id: int, word: str) -> bool:
    word_lower = word.strip().lower()
    existing = await get_banned_words(user_id)
    to_remove = None
    for w in existing:
        if w.lower() == word_lower:
            to_remove = w
            break
    if not to_remove:
        return False
    await banned_words_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"words": to_remove}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return True


async def remove_banned_word_by_index(user_id: int, index: int) -> bool:
    existing = await get_banned_words(user_id)
    if index < 0 or index >= len(existing):
        return False
    word = existing[index]
    await banned_words_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"words": word}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return True


async def clear_banned_words(user_id: int):
    await banned_words_collection.update_one(
        {"user_id": user_id},
        {"$set": {"words": [], "updated_at": datetime.utcnow()}},
        upsert=True
    )


def check_banned_words(text: str, banned_words: List[str]) -> bool:
    if not text or not banned_words:
        return False
    text_lower = text.lower()
    for word in banned_words:
        if word.lower() in text_lower:
            return True
    return False


def can_delete_now(worker_key: str) -> bool:
    now = datetime.utcnow()
    paused_until = _delete_paused_until.get(worker_key)
    if paused_until and now < paused_until:
        return False
    cutoff = now - timedelta(seconds=BANNED_DELETE_WINDOW)
    timestamps = _delete_timestamps[worker_key]
    _delete_timestamps[worker_key] = [t for t in timestamps if t > cutoff]
    if len(_delete_timestamps[worker_key]) >= BANNED_DELETE_RATE_LIMIT:
        _delete_paused_until[worker_key] = now + timedelta(seconds=BANNED_DELETE_PAUSE)
        _delete_timestamps[worker_key] = []
        return False
    return True


def record_deletion(worker_key: str):
    _delete_timestamps[worker_key].append(datetime.utcnow())


async def toggle_offline_mode(user_id: int, enabled: bool):
    await autoreply_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "offline_mode": enabled,
            "last_updated": datetime.utcnow()
        }},
        upsert=True
    )


async def set_offline_text(user_id: int, text: str):
    await autoreply_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "offline_text": text,
            "last_updated": datetime.utcnow()
        }},
        upsert=True
    )


def get_offline_message(settings: dict) -> str:
    text = settings.get("offline_text", "")
    if not text:
        return DEFAULT_OFFLINE_TEXT
    return text


async def can_send_offline(owner_id: int, worker_id: int, peer_id: int) -> bool:
    log_entry = await offline_log_collection.find_one({
        "owner_id": owner_id,
        "worker_id": worker_id,
        "peer_id": peer_id
    })
    if log_entry:
        last_sent = log_entry.get("last_sent")
        if last_sent:
            cutoff = datetime.utcnow() - timedelta(minutes=DEFAULT_OFFLINE_COOLDOWN_MINUTES)
            if last_sent > cutoff:
                return False
    return True


async def mark_offline_sent(owner_id: int, worker_id: int, peer_id: int):
    await offline_log_collection.update_one(
        {"owner_id": owner_id, "worker_id": worker_id, "peer_id": peer_id},
        {"$set": {"last_sent": datetime.utcnow()}},
        upsert=True
    )
