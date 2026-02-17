from datetime import datetime, timezone

from pyrogram import Client, filters

import database
from config import ADMIN_IDS, PRIVATE_INVITE_LINK


async def _require_admin(message) -> bool:
    return await database.is_admin(message.from_user.id, ADMIN_IDS)


async def _send_access_links(client: Client, user_id: int):
    parts = ["✅ ᴀᴄᴄᴇss ᴀᴄᴛɪᴠᴀᴛᴇᴅ"]
    if PRIVATE_INVITE_LINK:
        parts.append(f"✅ ᴘʀɪᴠᴀᴛᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ (ʀᴇᴀᴅ-ᴏɴʟʏ)\n{PRIVATE_INVITE_LINK}")
    await client.send_message(user_id, "\n\n".join(parts))


def register(app: Client):
    @app.on_message(filters.command("adduser") & filters.private)
    async def add_user(client: Client, message):
        if not await _require_admin(message):
            return
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply_text("❌ ᴜsᴀɢᴇ: /adduser user_id days")
            return
        user_id = int(parts[1])
        days = int(parts[2])
        expiry = await database.activate_plan(user_id, days, message.from_user.id)
        await message.reply_text(f"✅ ᴀᴅᴅᴇᴅ {user_id} ᴛɪʟʟ {expiry.isoformat()}")
        await _send_access_links(client, user_id)

    @app.on_message(filters.command("removeuser") & filters.private)
    async def remove_user(client: Client, message):
        if not await _require_admin(message):
            return
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("❌ ᴜsᴀɢᴇ: /removeuser user_id")
            return
        user_id = int(parts[1])
        await database.remove_plan(user_id)
        await message.reply_text(f"✅ ʀᴇᴍᴏᴠᴇᴅ ᴘʟᴀɴ ғᴏʀ {user_id}")
        try:
            await client.send_message(user_id, "❌ ʏᴏᴜʀ ᴘʟᴀɴ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ.")
        except Exception:
            pass

    @app.on_message(filters.command("checkplan") & filters.private)
    async def check_plan(_, message):
        if not await _require_admin(message):
            return
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("❌ ᴜsᴀɢᴇ: /checkplan user_id")
            return
        user_id = int(parts[1])
        expiry = await database.get_plan_expiry(user_id)
        if not expiry:
            await message.reply_text("❌ ɴᴏ ᴘʟᴀɴ ғᴏᴜɴᴅ.")
            return
        status = "✅ ᴀᴄᴛɪᴠᴇ" if expiry > datetime.now(timezone.utc) else "❌ ᴇxᴘɪʀᴇᴅ"
        await message.reply_text(f"👤 ᴜsᴇʀ {user_id}: {status}\n📅 ᴜɴᴛɪʟ {expiry.isoformat()}")

    @app.on_message(filters.command("extend") & filters.private)
    async def extend_plan(client: Client, message):
        if not await _require_admin(message):
            return
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply_text("❌ ᴜsᴀɢᴇ: /extend user_id days")
            return
        user_id = int(parts[1])
        days = int(parts[2])
        expiry = await database.extend_plan(user_id, days)
        await message.reply_text(f"✅ ᴇxᴛᴇɴᴅᴇᴅ {user_id} ᴛɪʟʟ {expiry.isoformat()}")
        await _send_access_links(client, user_id)
