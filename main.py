# (c) @RoyalKrrishna

from os import link
from telethon import Button
from configs import Config
from pyrogram import Client, idle
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from plugins.tgraph import *
from helpers import *
from telethon import TelegramClient, events
import urllib.parse
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import nest_asyncio

tbot = TelegramClient('mdisktelethonbot', Config.API_ID, Config.API_HASH).start(bot_token=Config.BOT_TOKEN)
client = TelegramClient(StringSession( Config.USER_SESSION_STRING), Config.API_ID, Config.API_HASH)

if Config.REPLIT:
    from threading import Thread

    from flask import Flask, jsonify
    
    app = Flask('')
    
    @app.route('/')
    def main():
        res = {
            "status":"running",
            "hosted":"replit.com",
            "repl":Config.REPLIT,
        }
        
        return jsonify(res)

    def run():
      app.run(host="0.0.0.0", port=8000)
    
    def keep_alive():
      server = Thread(target=run)
      server.start()

async def ping_server():
    sleep_time = Config.PING_INTERVAL
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(Config.REPLIT) as resp:
                    logging.info(f"Pinged server with response: {resp.status}")
        except TimeoutError:
            logging.warning("Couldn't connect to the site URL..!")
        except Exception:
            traceback.print_exc()


async def get_user_join(id):
    if Config.FORCE_SUB == "False":
        return True

    ok = True
    try:
        await tbot(GetParticipantRequest(channel=int(Config.UPDATES_CHANNEL), participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok


@tbot.on(events.NewMessage(incoming=True))
async def message_handler(event):

    if event.message.post:
        return

    print("\n")
    print("Message Received: " + event.text)
    # if event.is_channel:return
    if event.text.startswith("/"):return

    # Force Subscription
    if  not await get_user_join(event.sender_id):
        haha = await event.reply(f'''**Hey! {event.sender.first_name} 😃**

**You Have To Join Our Update Channel To Use Me ✅**

**Click Bellow Button To Join Now.👇🏻**''', buttons=Button.url('🍿Updates Channel🍿', f'https://t.me/{Config.UPDATES_CHANNEL_USERNAME}'))
        await asyncio.sleep(Config.AUTO_DELETE_TIME)
        return await haha.delete()

    
    print("Group: " + str(event.is_group))
    print("Channel: " + str(event.is_channel))
    args = event.text
    args = await validate_q(args)

    print("Search Query: {args}".format(args=args))
    print("\n")
    
    if not args:
        return

    txt = await event.reply('**Searching For "{}" 🔍**'.format(event.text))

    try:
        search = []
        async for i in AsyncIter(args.split()):
            search_msg = client.iter_messages(Config.CHANNEL_ID, limit=5, search=i)
            search.append(search_msg)

        username = Config.UPDATES_CHANNEL_USERNAME
        answer = f'**Join** [@{username}](https://telegram.me/{username}) \n\n'

        c = 0

        async for msg_list in AsyncIter(search):
            async for msg in msg_list:
                c += 1
                f_text = msg.text.replace("*", "")

  #              if event.is_group or event.is_channel:
  #                 f_text = await group_link_convertor(event.chat_id, f_text)

                f_text = await link_to_hyperlink(f_text)
                answer += f'\n\n**✅ PAGE {c}:**\n\n━━━━━━━━━\n\n' + '' + f_text.split("\n", 1)[0] + '' + '\n\n' + '' + f_text.split("\n", 2)[
                    -1] 
                
            # break
        finalsearch = []
        async for msg in AsyncIter(search):
            finalsearch.append(msg)

        if c <= 0:
            answer = f'''**No Results Found For {event.text}**

**Type Only Movie Name 💬**
**Check Spelling On** [Google](http://www.google.com/search?q={event.text.replace(' ', '%20')}%20Movie) 🔍
'''

            newbutton = [Button.url('Click To Check Spelling ✅',
                                    f'http://www.google.com/search?q={event.text.replace(" ", "%20")}%20Movie')], [
                            Button.url('Click To Check Release Date 📅',
                                    f'http://www.google.com/search?q={event.text.replace(" ", "%20")}%20Movie%20Release%20Date')], [
                            Button.url('👉 Search Here 👈',
                                    f'https://amzn.to/3ykSzxC')]
            await txt.delete()
            result = await event.reply(answer, buttons=newbutton, link_preview=False)
            await asyncio.sleep(Config.AUTO_DELETE_TIME)
            await event.delete()
            return await result.delete()
        else:
            pass

        answer += f"\n\n**Uploaded By @{Config.UPDATES_CHANNEL_USERNAME}**"
        answer = await replace_username(answer)
        html_content = await markdown_to_html(answer)
        html_content = await make_bold(html_content)
        tgraph_result = await telegraph_handler(
            html=html_content,
            title=event.text,
            author=Config.BOT_USERNAME
        )
        message = f'**Click Here 👇 For "{event.text}"**\n\n[🍿🎬 {str(event.text).upper()}\n🍿🎬 {str("Click me for results").upper()}]({tgraph_result})'
        button =  [Button.url('❓How To Open Link❓',
                                    f'https://t.me/iP_Update/8')], [
                            Button.url('👉 Search Here 👈',
                                    f'https://amzn.to/3MmfpIu')]

        await txt.delete()
        result = await event.reply(message, buttons=button, link_preview=False)
        await asyncio.sleep(Config.AUTO_DELETE_TIME)
        await event.delete()
        return await result.delete()

    except Exception as e:
        print(e)
        await txt.delete()
        result = await event.reply("**Some Error While Searching...‼️\n\nReport @RoyalKrrishn 🥷**")
        await asyncio.sleep(Config.AUTO_DELETE_TIME)
        await event.delete() 
        return await result.delete()


async def escape_url(str):
    escape_url = urllib.parse.quote(str)
    return escape_url


# Bot Client for Inline Search
class Bot(Client):

    def __init__(self):
        super().__init__(
        Config.BOT_SESSION_NAME,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=Config.BOT_TOKEN,
        plugins=dict(root="plugins")
        )

    def start(self):
        if Config.REPLIT:
            keep_alive()
            # ping_server()
        super().start()
        print('Bot started')

    def stop(self, *args):
        super().stop()
        print('Bot Stopped Bye')

print()
print("-------------------- Initializing Telegram Bot --------------------")
# Start Clients

tg_app = Bot()
tg_app.start()

print("------------------------------------------------------------------")
print()
print(f"""
 _____________________________________________   
|                                             |  
|          Deployed Successfully              |  
|              Join @{Config.UPDATES_CHANNEL_USERNAME}                 |
|_____________________________________________|
    """)

# User.start()
nest_asyncio.apply()

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is running", "channel": f"@{Config.UPDATES_CHANNEL_USERNAME}"}

@app.get("/search")
async def search(query: str = Query(..., min_length=1)):
    try:
        results = []
        async for msg in client.iter_messages(Config.CHANNEL_ID, search=query, limit=5):
            if msg.text:
                title_line = msg.text.split("\n", 1)[0]
                rest = msg.text.split("\n", 1)[-1]
                linkified = await link_to_hyperlink(msg.text)
                results.append({
                    "title": title_line.strip(),
                    "body": rest.strip(),
                    "formatted": linkified
                })
        if not results:
            return JSONResponse({"message": "No results found."}, status_code=404)
        return {"query": query, "results": results}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

async def main():
    with tbot, client:
        await asyncio.gather(
            tbot.run_until_disconnected(),
            client.run_until_disconnected()
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
