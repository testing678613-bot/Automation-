import asyncio
from datetime import datetime, timezone

import database
from config import EXPIRY_CHECK_SECONDS, PRIVATE_CHANNEL_ID, REQUIRED_CHANNELS


async def revoke_user_access(app, user_id: int):
    channels = await database.get_required_channels(REQUIRED_CHANNELS)
    for channel in channels:
        try:
            await app.ban_chat_member(channel, user_id)
            await app.unban_chat_member(channel, user_id)
        except Exception:
            continue

    if PRIVATE_CHANNEL_ID:
        try:
            await app.ban_chat_member(PRIVATE_CHANNEL_ID, user_id)
            await app.unban_chat_member(PRIVATE_CHANNEL_ID, user_id)
        except Exception:
            pass


async def expiry_worker(app):
    while True:
        now = datetime.now(timezone.utc)
        cursor = await database.get_expired_users(now)
        async for user in cursor:
            user_id = user["user_id"]
            await revoke_user_access(app, user_id)
            await database.remove_plan(user_id)
            try:
                await app.send_message(user_id, "❌ ᴘʟᴀɴ ᴇxᴘɪʀᴇᴅ. ᴀᴄᴄᴇss ʀᴇᴠᴏᴋᴇᴅ.")
            except Exception:
                pass
        await asyncio.sleep(EXPIRY_CHECK_SECONDS)
