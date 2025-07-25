from telethon import TelegramClient, events
from fastapi import FastAPI
import uvicorn
import asyncio
import re

from configs import Config

API_ID = Config.API_ID
API_HASH = Config.API_HASH
BOT_TOKEN = Config.BOT_TOKEN
BOT_USERNAME = Config.BOT_USERNAME
SOURCE_CHANNEL = Config.SOURCE_CHANNEL  # e.g., "demo360xyz"

# Start Telethon bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot is running", "website": Config.MOVIE_WEBSITE}

@app.get("/search")
async def search_movie(query: str):
    if not query:
        return {"results": []}

    results = []

    async for message in bot.iter_messages(SOURCE_CHANNEL, search=query, limit=20):
        if not message or not message.text:
            continue

        title = message.text.split('\n')[0].strip()
        buttons = []

        # Extract quality-wise download links from message
        for line in message.text.splitlines():
            match = re.search(r'(480p|720p|1080p|4K).*(http[s]?://\S+)', line, re.IGNORECASE)
            if match:
                label = match.group(1).upper()
                link = match.group(2)
                buttons.append(f"{label} - {link}")

        if buttons:
            results.append({
                "title": title,
                "links": buttons  # send all qualities now
            })

    return {"results": results}

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(Config.START_MSG)

# Combine both (FastAPI + Telethon)
async def main():
    print("Starting bot and API server...")
    await bot.start()
    await bot.run_until_disconnected()

def start():
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    uvicorn.run(app, host="0.0.0.0", port=10000)

if __name__ == "__main__":
    start()
