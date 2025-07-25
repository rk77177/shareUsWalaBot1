import os
import asyncio
from fastapi import FastAPI, Request
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError
import uvicorn

# Environment from Render (no dotenv)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")  # public username or full ID

tbot = TelegramClient("bot", API_ID, API_HASH)
app = FastAPI()
channel_entity = None  # Global

# ========== Search Logic ==========
async def search_files(query):
    global channel_entity

    results = []
    async for msg in tbot.iter_messages(channel_entity, search=query, limit=10):
        if msg.text:
            results.append({
                "title": msg.text.split('\n')[0][:100],
                "link": f"https://t.me/c/{str(channel_entity.channel_id)}/{msg.id}"
            })

    return results

# ========== Telegram Bot ==========
async def setup_bot():
    @tbot.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        await event.respond("✅ Bot is alive!")

# ========== API Routes ==========
@app.get("/")
async def home():
    return {"status": "✅ Bot is running"}

@app.get("/search")
async def search_endpoint(query: str):
    results = await search_files(query)
    return {"query": query, "results": results}

# ========== Startup ==========
@app.on_event("startup")
async def on_startup():
    global channel_entity

    print("🔄 Starting bot...")
    await tbot.start(bot_token=BOT_TOKEN)
    await setup_bot()

    try:
        channel_entity = await tbot.get_entity(SOURCE_CHANNEL)
        print(f"✅ Channel loaded: {SOURCE_CHANNEL}")
    except (ChannelPrivateError, UsernameNotOccupiedError, ValueError) as e:
        print(f"❌ Failed to load channel: {e}")
        raise

    print("✅ Bot and FastAPI ready")

# ========== Run ==========
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
