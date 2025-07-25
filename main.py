import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from telethon import TelegramClient, events
from telethon.tl.types import Message
import uvicorn

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))
SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL"))

# Initialize Telegram bot client
tbot = TelegramClient("bot", API_ID, API_HASH)

# FastAPI app
app = FastAPI()

# ===== SEARCH FUNCTION =====

async def search_files(query: str):
    results = []
    async for msg in tbot.iter_messages(SOURCE_CHANNEL, search=query, limit=20):
        if msg.message:
            # Parse message like: Movie Title (2022) 720p - https://link
            parts = msg.message.split(" - ")
            if len(parts) == 2:
                title = parts[0].strip()
                link = parts[1].strip()
                results.append({"title": title, "link": link})
    return results

# ===== FASTAPI ROUTES =====

@app.get("/")
async def root():
    return {"status": "✅ Bot is running!"}

@app.get("/search")
async def search(query: str):
    results = await search_files(query)
    return {"query": query, "results": results}

# ===== TELETHON BOT SETUP =====

async def setup_bot():
    @tbot.on(events.NewMessage(pattern="/start"))
    async def start_handler(event):
        await event.respond("✅ Bot is alive!")

# ===== APP STARTUP =====

@app.on_event("startup")
async def startup():
    await tbot.start(bot_token=BOT_TOKEN)
    await setup_bot()
    print("✅ Bot started with FastAPI")

# ===== MAIN =====

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
