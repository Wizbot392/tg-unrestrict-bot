import os, asyncio, time
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- 1. RENDER PORT HEARTBEAT ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Status: Running & High-Speed"

def run_flask(): app.run(host='0.0.0.0', port=10000)

# --- 2. CREDENTIALS ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# --- 3. PROGRESS LOGIC ---
async def progress_bar(current, total, status_msg, action):
    percent = current * 100 / total
    if int(percent) % 10 == 0: # Update every 10%
        try:
            bar = '■' * int(percent // 10) + '□' * (10 - int(percent // 10))
            await status_msg.edit(f"🚀 **{action}**\n`|{bar}|` **{percent:.1f}%**")
        except: pass

# --- 4. MAIN HANDLER ---
@client.on(events.NewMessage(incoming=True, outgoing=True))
async def handler(event):
    if event.is_private and "t.me/" in event.text:
        me = await client.get_me()
        if event.chat_id == me.id:
            status = await event.reply("📂 **Fetching Original File...**")
            try:
                link = event.text.split('/')
                msg_id, chat_username = int(link[-1]), link[-2]
                target_msg = await client.get_messages(chat_username, ids=msg_id)

                if target_msg and target_msg.media:
                    # Capture the original name
                    name = target_msg.file.name or "unlocked_file.mp4"
                    
                    # High-Speed Download
                    path = await client.download_media(
                        target_msg,
                        progress_callback=lambda c, t: client.loop.create_task(
                            progress_bar(c, t, status, f"📥 Down: {name}")
                        )
                    )
                    
                    # High-Speed Upload as File (Document)
                    await status.edit(f"📤 **Sending original format...**")
                    await client.send_file(
                        'me', 
                        path, 
                        force_document=True, # Keeps it in file format
                        file_name=name,      # Keeps original name
                        caption=f"✅ **Unlocked:** `{name}`",
                        part_size_kb=512,
                        progress_callback=lambda c, t: client.loop.create_task(
                            progress_bar(c, t, status, "📤 Uploading")
                        )
                    )
                    
                    if os.path.exists(path): os.remove(path)
                    await status.delete()
                else:
                    await status.edit("❌ No media found in link.")
            except Exception as e:
                await status.edit(f"❌ Error: {str(e)}")

# --- 5. START ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    client.start()
    client.run_until_disconnected()
