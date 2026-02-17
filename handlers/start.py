from datetime import datetime, timezone

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import database
from config import ADMIN_USERNAME, FORCE_SUB_FOLDER_LINK, REQUIRED_CHANNELS, STARS_ADMIN

LANG_TEXT = {
    "en": {
        "choose_lang": "🌍 sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ / भाषा चुनें",
        "join_first": "🔔 ᴊᴏɪɴ thid cʜᴀɴɴᴇʟs ғɪʀsᴛ",
        "dashboard": (
            "🔥 ᴅᴇᴠɪʟ ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ 😈\n\n"
            "💎 ᴘʀᴇᴍɪᴜᴍ ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ ʙᴏᴛ\n"
            "🤖 ᴀᴜᴛᴏ ʀᴇᴘʟʏ • 🌙 ᴏғғʟɪɴᴇ ᴍᴏᴅᴇ • 🛡 sᴍᴀʀᴛ ғɪʟᴛᴇʀs\n\n"
            "🔒 ᴀᴄᴄᴇss ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴʟʏ ᴡɪᴛʜ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ."
        ),
        "plans": (
            "💎 ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs\n\n"
            "💳 ₹50 / ᴍᴏɴᴛʜ (ᴜᴘɪ)\n"
            "💰 $1 (ᴄʀʏᴘᴛᴏ ʙɪɴᴀɴᴄᴇ)\n"
            "⭐ 25 sᴛᴀʀs"
        ),
        "plan_active": "✅ ᴘʟᴀɴ ᴀᴄᴛɪᴠᴇ\n📅 ᴇxᴘɪʀʏ: {expiry}",
        "plan_inactive": "❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ\n📩 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ.",
        "help": "ℹ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ғᴏʀ sᴜᴘᴘᴏʀᴛ.",
        "lang_updated": "✅ ʟᴀɴɢᴜᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ.",
        "select_lang_first": "🌍 sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ ғɪʀsᴛ",
        "checked": "✅ ᴄʜᴇᴄᴋᴇᴅ",
        "still_not_joined": "❌ sᴛɪʟʟ ɴᴏᴛ ᴊᴏɪɴᴇᴅ",
        "no_active_plan": "❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ",
        "autoreply_enabled": "✅ ᴀᴜᴛᴏʀᴇᴘʟʏ ᴇɴᴀʙʟᴇᴅ",
        "autoreply_disabled": "✅ ᴀᴜᴛᴏʀᴇᴘʟʏ ᴅɪsᴀʙʟᴇᴅ",
        "active_plan_required": "🔒 ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ ʀᴇǫᴜɪʀᴇᴅ.",
        "login_success": "✅ ᴀᴜᴛᴏʀᴇᴘʟʏ ʟᴏɢɪɴ sᴜᴄᴄᴇssғᴜʟ.",
        "logout_success": "✅ ᴀᴜᴛᴏʀᴇᴘʟʏ ʟᴏɢᴏᴜᴛ sᴜᴄᴄᴇssғᴜʟ.",
        "settings_title": "⚙ sᴇᴛᴛɪɴɢs",
    },
    "hi": {
        "choose_lang": "🌍 sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ / भाषा चुनें",
        "join_first": "🔔 पहले चैनल जॉइन करें",
        "dashboard": (
            "🔥 डेविल ऑटोमेशन 😈\n\n"
            "प्रीमियम ऑटोमेशन बॉट\n"
            "ऑटो रिप्लाई • ऑफलाइन मोड • स्मार्ट फिल्टर्स\n\n"
            "एक्सेस केवल सक्रिय प्लान के साथ उपलब्ध है।"
        ),
        "plans": (
            "💎 उपलब्ध प्लान\n\n"
            "₹50 / महीना (UPI)\n"
            "$1 (क्रिप्टो Binance)\n"
            "⭐ 25 स्टार्स"
        ),
        "plan_active": "✅ प्लान सक्रिय\nसमाप्ति: {expiry}",
        "plan_inactive": "❌ कोई सक्रिय प्लान नहीं\nसक्रिय करने के लिए एडमिन से संपर्क करें।",
        "help": "सहायता के लिए एडमिन से संपर्क करें।",
        "lang_updated": "भाषा अपडेट हो गई।",
        "select_lang_first": "पहले भाषा चुनें",
        "checked": "जांच हो गई",
        "still_not_joined": "अभी तक जॉइन नहीं किया",
        "no_active_plan": "कोई सक्रिय प्लान नहीं",
        "autoreply_enabled": "ऑटो रिप्लाई चालू हो गया",
        "autoreply_disabled": "ऑटो रिप्लाई बंद हो गया",
        "active_plan_required": "सक्रिय प्लान आवश्यक है।",
        "login_success": "✅ ऑटो रिप्लाई लॉगिन सफल।",
        "logout_success": "✅ ऑटो रिप्लाई लॉगआउट सफल।",
        "settings_title": "⚙ सेटिंग्स",
    },
}


def lang_keyboard(back_to_dashboard: bool = False):
    rows = [
        [InlineKeyboardButton("🇬🇧 ᴇɴɢʟɪsʜ", callback_data="lang_en")],
        [InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi")],
    ]
    if back_to_dashboard:
        rows.append([InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="menu_dashboard")])
    return InlineKeyboardMarkup(rows)


def join_keyboard():
    buttons = []

    # Individual channel buttons
    for channel in REQUIRED_CHANNELS:
        buttons.append(
            [InlineKeyboardButton("🔔 Join Channel", url=channel["link"])]
        )

    # Folder button (Join all at once)
    if FORCE_SUB_FOLDER_LINK:
        buttons.append(
            [InlineKeyboardButton("📂 Join All Channels", url=FORCE_SUB_FOLDER_LINK)]
        )

    # Check & Abort
    buttons.append(
        [InlineKeyboardButton("🔄 Check Again", callback_data="check_join")]
    )
    buttons.append(
        [InlineKeyboardButton("❌ Abort", callback_data="abort")]
    )

    return InlineKeyboardMarkup(buttons)
    )


def dashboard_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📦 ᴘʟᴀɴs", callback_data="menu_plans"),
                InlineKeyboardButton("👤 ᴍʏ ᴘʟᴀɴ", callback_data="menu_myplan"),
            ],
            [
                InlineKeyboardButton("⚙ sᴇᴛᴛɪɴɢs", callback_data="menu_settings"),
                InlineKeyboardButton("ℹ ʜᴇʟᴘ", callback_data="menu_help"),
            ],
        ]
    )


def plans_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💳 ʙᴜʏ ᴠɪᴀ ᴜᴘɪ", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("💰 ʙᴜʏ ᴠɪᴀ ʙɪɴᴀɴᴄᴇ", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("⭐ ʙᴜʏ ᴠɪᴀ sᴛᴀʀs", url=f"https://t.me/{STARS_ADMIN.lstrip('@')}")],
            [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="menu_dashboard")],
        ]
    )


def myplan_keyboard(active: bool):
    rows = []
    if not active:
        rows.append([InlineKeyboardButton("📦 ᴘʟᴀɴs", callback_data="menu_plans")])
    rows.append([InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="menu_dashboard")])
    return InlineKeyboardMarkup(rows)


def settings_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 ᴄʜᴀɴɢᴇ ʟᴀɴɢᴜᴀɢᴇ", callback_data="menu_language_change")],
            [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="menu_dashboard")],
        ]
    )


def help_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📩 ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton("⬅ ʙᴀᴄᴋ", callback_data="menu_dashboard")],
        ]
    )


def active_controls_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔐 ʟᴏɢɪɴ", callback_data="do_login"), InlineKeyboardButton("🔓 ʟᴏɢᴏᴜᴛ", callback_data="do_logout")]]
    )


async def is_joined_all(client: Client, user_id: int) -> bool:
    channels = await database.get_required_channels(REQUIRED_CHANNELS)
    for channel in channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in {"left", "kicked"}:
                return False
        except Exception:
            return False
    return True


async def _get_user_lang(user_id: int) -> str:
    user = await database.get_user(user_id)
    return user.get("language", "en")


async def show_start(client: Client, message, user):
    if not user.get("language"):
        await message.reply_text(LANG_TEXT["en"]["choose_lang"], reply_markup=lang_keyboard())
        return

    if not await is_joined_all(client, user["user_id"]):
        lang = user["language"]
        await message.reply_text(LANG_TEXT[lang]["join_first"], reply_markup=join_keyboard())
        return

    lang = user["language"]
    await message.reply_text(LANG_TEXT[lang]["dashboard"], reply_markup=dashboard_keyboard())


def register(app: Client):
    @app.on_message(filters.command("start") & filters.private)
    async def start_handler(client: Client, message):
        user_id = message.from_user.id
        await database.upsert_user(user_id=user_id)
        user = await database.get_user(user_id)
        await show_start(client, message, user)

    @app.on_callback_query(filters.regex(r"^lang_(en|hi)$"))
    async def set_language(client: Client, callback_query):
        lang = callback_query.data.split("_")[1]
        user_id = callback_query.from_user.id
        await database.set_language(user_id, lang)
        await callback_query.answer(LANG_TEXT[lang]["lang_updated"])

        user = await database.get_user(user_id)
        await callback_query.message.delete()
        await show_start(client, callback_query.message, user)

    @app.on_callback_query(filters.regex(r"^check_join$"))
    async def check_join(client: Client, callback_query):
        user = await database.get_user(callback_query.from_user.id)
        lang = user.get("language", "en")
        if not user.get("language"):
            await callback_query.answer(LANG_TEXT[lang]["select_lang_first"], show_alert=True)
            return

        if await is_joined_all(client, callback_query.from_user.id):
            await callback_query.answer(LANG_TEXT[lang]["checked"])
            await callback_query.message.delete()
            refreshed_user = await database.get_user(callback_query.from_user.id)
            await show_start(client, callback_query.message, refreshed_user)
            return

        await callback_query.answer(LANG_TEXT[lang]["still_not_joined"], show_alert=True)

    @app.on_callback_query(filters.regex(r"^menu_dashboard$"))
    async def menu_dashboard(_, callback_query):
        user = await database.get_user(callback_query.from_user.id)
        lang = user.get("language", "en")
        await callback_query.answer()
        await callback_query.message.edit_text(LANG_TEXT[lang]["dashboard"], reply_markup=dashboard_keyboard())

    @app.on_callback_query(filters.regex(r"^menu_plans$"))
    async def menu_plans(_, callback_query):
        user = await database.get_user(callback_query.from_user.id)
        lang = user.get("language", "en")
        await callback_query.answer()
        await callback_query.message.edit_text(LANG_TEXT[lang]["plans"], reply_markup=plans_keyboard())

    @app.on_callback_query(filters.regex(r"^menu_myplan$"))
    async def menu_myplan(_, callback_query):
        user_id = callback_query.from_user.id
        lang = await _get_user_lang(user_id)
        expiry = await database.get_plan_expiry(user_id)

        active = bool(expiry and expiry > datetime.now(timezone.utc))
        if active:
            text = LANG_TEXT[lang]["plan_active"].format(expiry=expiry.strftime("%d/%m/%Y"))
        else:
            text = LANG_TEXT[lang]["plan_inactive"]

        await callback_query.answer()
        await callback_query.message.edit_text(text, reply_markup=myplan_keyboard(active))

    @app.on_callback_query(filters.regex(r"^menu_settings$"))
    async def menu_settings(_, callback_query):
        lang = await _get_user_lang(callback_query.from_user.id)
        await callback_query.answer()
        await callback_query.message.edit_text(LANG_TEXT[lang]["settings_title"], reply_markup=settings_keyboard())

    @app.on_callback_query(filters.regex(r"^menu_language_change$"))
    async def menu_language_change(_, callback_query):
        lang = await _get_user_lang(callback_query.from_user.id)
        await callback_query.answer()
        await callback_query.message.edit_text(LANG_TEXT[lang]["choose_lang"], reply_markup=lang_keyboard(back_to_dashboard=True))

    @app.on_callback_query(filters.regex(r"^menu_help$"))
    async def menu_help(_, callback_query):
        lang = await _get_user_lang(callback_query.from_user.id)
        await callback_query.answer()
        await callback_query.message.edit_text(LANG_TEXT[lang]["help"], reply_markup=help_keyboard())

    @app.on_callback_query(filters.regex(r"^abort$"))
    async def abort_menu(client: Client, callback_query):
        await callback_query.answer()
        await callback_query.message.delete()
        user = await database.get_user(callback_query.from_user.id)
        await show_start(client, callback_query.message, user)

    @app.on_callback_query(filters.regex(r"^do_login$"))
    async def do_login(_, callback_query):
        from autoreply import toggle_autoreply

        user_id = callback_query.from_user.id
        lang = await _get_user_lang(user_id)
        if not await database.has_active_plan(user_id):
            await callback_query.answer(LANG_TEXT[lang]["no_active_plan"], show_alert=True)
            return

        await toggle_autoreply(user_id, True)
        await callback_query.answer(LANG_TEXT[lang]["autoreply_enabled"])

    @app.on_callback_query(filters.regex(r"^do_logout$"))
    async def do_logout(_, callback_query):
        from autoreply import toggle_autoreply

        lang = await _get_user_lang(callback_query.from_user.id)
        await toggle_autoreply(callback_query.from_user.id, False)
        await callback_query.answer(LANG_TEXT[lang]["autoreply_disabled"])

    @app.on_message(filters.command("help") & filters.private)
    async def help_command(_, message):
        lang = await _get_user_lang(message.from_user.id)
        await message.reply_text(LANG_TEXT[lang]["help"], reply_markup=help_keyboard())

    @app.on_message(filters.command("login") & filters.private)
    async def login_command(_, message):
        from autoreply import toggle_autoreply

        user_id = message.from_user.id
        lang = await _get_user_lang(user_id)
        if not await database.has_active_plan(user_id):
            await message.reply_text(LANG_TEXT[lang]["active_plan_required"])
            return

        await toggle_autoreply(user_id, True)
        await message.reply_text(LANG_TEXT[lang]["login_success"], reply_markup=active_controls_keyboard())

    @app.on_message(filters.command("logout") & filters.private)
    async def logout_command(_, message):
        from autoreply import toggle_autoreply

        lang = await _get_user_lang(message.from_user.id)
        await toggle_autoreply(message.from_user.id, False)
        await message.reply_text(LANG_TEXT[lang]["logout_success"])
