import os

API_ID = int(os.getenv("API_ID", "36875651"))
API_HASH = os.getenv("API_HASH", "3d373904bbb08c556daf7e1916430a02")

# ⚠️ For security, better to use environment variable instead of hardcoding
BOT_TOKEN = "8515397355:AAHN8eTngxxGNp3bE8fq18K3ZY1k4o7X0EE"

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ftm:ftm@cluster0.tseoajm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "devil_automation")

REQUIRED_CHANNELS = [
    {
        "id": -1003235695970,
        "link": "https://t.me/+_owE_oIQ7QYxZjc0"
    },
    {
        "id": -1003082810634,
        "link": "https://t.me/+ekws2PRJr6A1Mjg1"
    },
    {
        "id": -1002087228619,
        "link": "https://t.me/ftmbotzx"
    }
]

# Folder Force Subscribe Link
FORCE_SUB_FOLDER_LINK = "https://t.me/addlist/pBHjmByyOek0NTdk"

ADMIN_USERNAME = "@ftmservices"
STARS_ADMIN = "@GodImmortals"

PRIVATE_INVITE_LINK = os.getenv("PRIVATE_INVITE_LINK", "")
PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID", "0")) or REQUIRED_CHANNELS

# ✅ Updated Admin IDs
ADMIN_IDS = [
    6434458914,
    7355698464,
    6876433368
]

# Expiry Check Timer
EXPIRY_CHECK_SECONDS = 300
