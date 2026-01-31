import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- 1. FLASK WEB SERVER (To satisfy Render's port check) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_flask():
    # Render uses port 10000 by default
    app.run(host='0.0.0.0', port=10000)

# --- 2. TELETHON USERBOT SETUP ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def handler(event):
    # Triggers when you paste a link in your 'Saved Messages'
    if event.is_private and "t.me/" in event.text:
        me = await client.get_me()
        if event.chat_id == me.id:
            status = await event.reply("⚡ Cloud Link Detected...")
            try:
                # Extract link details
                link_parts = event.text.split('/')
                msg_id = int(link_parts[-1])
                chat_username = link_parts[-2]

                # Download file to Cloud RAM
                target_msg = await client.get_messages(chat_username, ids=msg_id)
                if target_msg and target_msg.media:
                    await status.edit("📥 Downloading in Cloud (Zero Phone Storage)...")
                    path = await client.download_media(target_msg)
                    
                    await status.edit("📤 Uploading Unrestricted Version...")
                    await client.send_file('me', path, caption="✅ File Unlocked")
                    
                    # Delete from Cloud immediately
                    if os.path.exists(path):
                        os.remove(path)
                    await status.delete()
                else:
                    await status.edit("❌ No file found in that link.")
            except Exception as e:
                await status.edit(f"❌ Error: {str(e)}")

# --- 3. EXECUTION ---
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Start Telegram Client
    print("Userbot is starting...")
    client.start()
    client.run_until_disconnected()
