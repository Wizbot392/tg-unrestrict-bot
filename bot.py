import os, asyncio, time
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession

# --- 1. RENDER HEARTBEAT ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot: Ultra-Fast Streaming Active"

def run_flask(): 
    # Render ብዙውን ጊዜ PORT 10000 ይጠቀማል
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CREDENTIALS ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

# Connection_retries እና ቀልጣፋ መስመር በመጠቀም
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH, sequential_updates=False)

# --- 3. FAST PROGRESS LOGIC ---
last_update_time = {}

async def progress_bar(current, total, status_msg, action, msg_id):
    now = time.time()
    # በየ 4 ሰከንዱ አንዴ ብቻ እንዲያድስ (Telegram እንዳያግደን)
    if msg_id in last_update_time and now - last_update_time[msg_id] < 4:
        return
    
    last_update_time[msg_id] = now
    percent = current * 100 / total
    bar = '■' * int(percent // 10) + '□' * (10 - int(percent // 10))
    
    try:
        await status_msg.edit(
            f"🚀 **{action}**\n"
            f"`|{bar}|` **{percent:.1f}%**\n"
            f"📦 **Size:** {current/1024/1024:.1f}/{total/1024/1024:.1f} MB"
        )
    except: pass

# --- 4. MAIN HANDLER ---
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handler(event):
    if "t.me/" in event.text:
        me = await client.get_me()
        if event.sender_id != me.id: return # ለራስህ ብቻ እንዲሰራ

        status = await event.reply("📂 **ያልተገደበ ፍጥነት በመጠቀም ላይ...**")
        try:
            # ሊንኩን መለየት (Private link handling)
            link_parts = event.text.split('/')
            msg_id = int(link_parts[-1])
            
            # ቻናሉን በ ID ወይም በ Username መለየት
            if "t.me/c/" in event.text:
                chat = int("-100" + link_parts[-2])
            else:
                chat = link_parts[-2]

            target_msg = await client.get_messages(chat, ids=msg_id)

            if target_msg and target_msg.media:
                name = target_msg.file.name or "file.mp4"
                
                # --- FAST DOWNLOAD ---
                # 'part_size_kb' መጨመር ፍጥነትን ይጨምራል
                path = await client.download_media(
                    target_msg,
                    progress_callback=lambda c, t: progress_bar(c, t, status, f"📥 Downloading: {name}", event.id)
                )
                
                # --- FAST UPLOAD ---
                await status.edit(f"📤 **በከፍተኛ ፍጥነት በመላክ ላይ...**")
                
                # 'me' (Saved Messages) ላይ ኦሪጅናል ስሙን ጠብቆ ይልካል
                await client.send_file(
                    'me', 
                    path, 
                    force_document=True,
                    file_name=name,
                    caption=f"✅ **Downloaded:** `{name}`",
                    progress_callback=lambda c, t: progress_bar(c, t, status, "📤 Uploading", event.id)
                )
                
                if os.path.exists(path): os.remove(path)
                await status.delete()
            else:
                await status.edit("❌ ፋይል አልተገኘም!")
        except Exception as e:
            await status.edit(f"❌ Error: {str(e)}")

# --- 5. START ---
if __name__ == "__main__":
    Thread(target=run_flask).start()
    client.start()
    print("Bot is fully optimized for speed!")
    client.run_until_disconnected()
