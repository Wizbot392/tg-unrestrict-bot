import os
import asyncio
import time
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- FLASK SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live"

def run_flask(): app.run(host='0.0.0.0', port=10000)

# --- TELETHON BOT ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- PROGRESS HELPER ---
async def progress_bar(current, total, status_msg, action):
    # Only update every 5% to avoid Telegram rate limits
    percent = current * 100 / total
    if int(percent) % 5 == 0:
        try:
            await status_msg.edit(f"🚀 **{action}**\n`[{'■' * int(percent // 10)}{'□' * (10 - int(percent // 10))}]` {percent:.1f}%")
        except:
            pass

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def handler(event):
    if event.is_private and "t.me/" in event.text:
        me = await client.get_me()
        if event.chat_id == me.id:
            status = await event.reply("🔎 Preparing Cloud Download...")
            try:
                link = event.text.split('/')
                msg_id = int(link[-1])
                chat_username = link[-2]

                target_msg = await client.get_messages(chat_username, ids=msg_id)
                if target_msg and target_msg.media:
                    # 1. DOWNLOAD
                    path = await client.download_media(
                        target_msg, 
                        progress_callback=lambda c, t: client.loop.create_task(
                            progress_bar(c, t, status, "Downloading to Cloud")
                        )
                    )
                    
                    # 2. UPLOAD
                    await status.edit("📤 Uploading to Saved Messages...")
                    await client.send_file(
                        'me', path, 
                        caption="✅ File Unlocked (Forwarding Enabled)",
                        progress_callback=lambda c, t: client.loop.create_task(
                            progress_bar(c, t, status, "Uploading to You")
                        )
                    )
                    
                    if os.path.exists(path): os.remove(path)
                    await status.delete()
                else:
                    await status.edit("❌ No media found.")
            except Exception as e:
                await status.edit(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    client.start()
    client.run_until_disconnected()
