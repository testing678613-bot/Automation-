import asyncio
import logging

from pyrogram import Client

from config import API_HASH, API_ID, BOT_TOKEN
from handlers import register_handlers
from scheduler import expiry_worker

logging.basicConfig(level=logging.INFO)

app = Client("devil-automation-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


async def run():
    register_handlers(app)
    await app.start()
    asyncio.create_task(expiry_worker(app))
    logging.info("Devil Automation bot started")
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(run())
