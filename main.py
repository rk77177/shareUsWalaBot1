import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telethon import TelegramClient, events
import uvicorn

# Load env variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Initialize Telegram client
tbot = TelegramClient("bot", API_ID, API_HASH)

# Initialize FastAPI
app = FastAPI()

# In-memory dummy search (replace with real search logic later)
async def search_files(query):
    # 👇 Dummy data for now
    return [
        {"title": "Example Movie 1", "link": "https://t.me/yourchannel/1"},
        {"title": "Example Movie 2", "link": "https://t.me/yourchannel/2"}
    ]

# ========== TELETHON HANDLERS ==========
async def setup_bot():
    @tbot.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        await event.respond("✅ Bot is alive!")
    
    @tbot.on(events.NewMessage)
    async def catch_all_handler(event):
        if event.text and "hi" in event.text.lower():
            await event.reply("Hello! 👋")

# ========== FASTAPI ROUTES ==========

@app.get("/")
async def home():
    return {"status": "✅ Bot is running"}

@app.get("/search")
async def search_endpoint(query: str):
    results = await search_files(query)
    return {"query": query, "results": results}

# ========== STARTUP EVENT ==========

@app.on_event("startup")
async def on_startup():
    print("🔄 Starting bot...")
    await tbot.start(bot_token=BOT_TOKEN)
    await setup_bot()
    print("✅ Bot started with FastAPI")

# ========== MAIN ==========

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
