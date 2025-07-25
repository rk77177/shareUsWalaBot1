from telethon import TelegramClient, events
from fastapi import FastAPI
import uvicorn
import asyncio
import os

from configs import Config

API_ID = Config.API_ID
API_HASH = Config.API_HASH
BOT_TOKEN = Config.BOT_TOKEN
BOT_USERNAME = Config.BOT_USERNAME

# Start Telethon bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot is running", "website": Config.MOVIE_WEBSITE}

@app.get("/search")
async def search_movie(query: str):
    return {"result": f"You searched for '{query}'. Implement search logic here."}

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(Config.START_MSG)

# Combine both (FastAPI + Telethon)
async def main():
    print("Starting bot and API server...")
    await bot.start()
    await bot.run_until_disconnected()

# Run FastAPI app in background and Telethon bot in main loop
def start():
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    uvicorn.run(app, host="0.0.0.0", port=10000)

if __name__ == "__main__":
    start()
