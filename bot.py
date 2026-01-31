import os, asyncio, time
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Flask for Render Port
app = Flask(__name__)
@app.route('/')
def home(): return "Bot Speed: Maximum"

def run_flask(): app.run(host='0.0.0.0', port=10000)

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

# Use 'cryptg' if installed for 10x speed
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

async def progress_bar(current, total, status_msg, action):
    percent = current * 100 / total
    # Update every 10% to save resources and speed up
    if int(percent) % 10 == 0:
        try:
            bar = '■' * int(percent // 10) + '□' * (10 - int(percent // 10))
            await status_msg.edit(f"⚡ **{action}**\n`|{bar}|` **{percent:.1f}%**")
        except: pass

@client.on(events.NewMessage(incoming=True, outgoing=True))
async def handler(event):
    if event.is_private and "t.me/" in event.text:
        me = await client.get_me()
        if event.chat_id == me.id:
            status = await event.reply("🚀 **High-Speed Mode Active...**")
            try:
                link = event.text.split('/')
                msg_id, chat_username = int(link[-1]), link[-2]
                target_msg = await client.get_messages(chat_username, ids=msg_id)

                if target_msg and target_msg.media:
                    # Optimized Download
                    path = await client.download_media(
                        target_msg,
                        progress_callback=lambda c, t: client.loop.create_task(
                            progress_bar(c, t, status, "⚡ Downloading")
                        )
                    )
                    
                    # Optimized Upload (Part size 512KB for 1GB+ files)
                    await status.edit("📤 **Finalizing Upload...**")
                    await client.send_file(
                        'me', path, 
                        caption="✅ File Unlocked",
                        part_size_kb=512,
                        progress_callback=lambda c, t: client.loop.create_task(
                            progress_bar(c, t, status, "⚡ Uploading")
                        )
                    )
                    if os.path.exists(path): os.remove(path)
                    await status.delete()
            except Exception as e:
                await status.edit(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    client.start()
    client.run_until_disconnected()
