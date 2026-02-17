from pyrogram import Client, filters

import database
from autoreply import *  # noqa: F401,F403


def register(app: Client):
    @app.on_message(filters.command("settemplate") & filters.private)
    async def set_template(_, message):
        if not await database.has_active_plan(message.from_user.id):
            await message.reply_text("🔒 ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ ʀᴇǫᴜɪʀᴇᴅ.")
            return
        template = message.text.split(maxsplit=1)
        if len(template) < 2:
            await message.reply_text("❌ ᴜsᴀɢᴇ: /settemplate ʏᴏᴜʀ ᴛᴇxᴛ")
            return
        await set_template_text(message.from_user.id, template[1])
        await message.reply_text("✅ ᴛᴇᴍᴘʟᴀᴛᴇ ᴜᴘᴅᴀᴛᴇᴅ.")

    @app.on_message(
        filters.private
        & filters.text
        & ~filters.command(["start", "help", "login", "logout", "settemplate", "adduser", "removeuser", "checkplan", "extend", "links"])
    )
    async def handle_autoreply(_, message):
        user_id = message.from_user.id
        if not await database.has_active_plan(user_id):
            return

        settings = await get_autoreply_settings(user_id)
        if not settings.get("enabled"):
            return

        text = message.text or ""
        if is_auto_reply_loop(text):
            return

        peer_id = message.chat.id

        if settings.get("offline_mode"):
            if not await can_send_offline(user_id, user_id, peer_id):
                return
            await message.reply_text(get_offline_message(settings))
            await mark_offline_sent(user_id, user_id, peer_id)
            return

        if not await can_reply_now(user_id, peer_id):
            return

        template = settings.get("template_text") or "🙏 ᴛʜᴀɴᴋs ғᴏʀ ʀᴇᴀᴄʜɪɴɢ ᴏᴜᴛ."
        rendered = render_template(
            template,
            first_name=message.from_user.first_name or "",
            username=message.from_user.username or "",
            chat_id=peer_id,
        )

        photo_file_id = settings.get("photo_file_id")
        if photo_file_id:
            await message.reply_photo(photo_file_id, caption=rendered)
        else:
            await message.reply_text(rendered)

        await mark_replied(user_id, peer_id)
