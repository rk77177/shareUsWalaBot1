import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_USERNAME = os.getenv("BOT_USERNAME")
    
    SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")  # 🔥 Add this line

    START_MSG = "Hi! I'm alive. Send a movie name to search."
    MOVIE_WEBSITE = os.getenv("MOVIE_WEBSITE", "https://uniquechatbot.blogspot.com")
