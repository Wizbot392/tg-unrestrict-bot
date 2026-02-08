import os, asyncio, time
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- 1. RENDER PORT FIX (ለ Render የግድ ነው) ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online and Ready!"

def run_flask():
    # Render PORT 10000 ወይም በራሱ የሚሰጠውን ይጠቀማል
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CREDENTIALS ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

# 'sequential_updates=False' ብዙ ስራ በአንድ ጊዜ እንዲሰራ ያደርጋል
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH, sequential_updates=False)

# --- 3. HIGH-SPEED PROGRESS BAR ---
async def progress_bar(current, total, status_msg, action):
    percent = current * 100 / total
    # በየ 10% ልዩነት ብቻ ሜሴጅ ኤዲት በማድረግ ፍጥነትን መጨመር
    if int(percent) % 10 == 0:
        try:
            bar = '■' * int(percent // 10) + '□' * (10 - int(percent // 10))
            await status_msg.edit(f"🚀 **{action}**\n`|{bar}|` **{percent:.1f}%**")
        except: pass

# --- 4. THE ULTIMATE HANDLER ---
# ማንኛውም የቴሌግራም ሊንክ ያለበት ሜሴጅ ሲመጣ ይሰራል
@client.on(events.NewMessage(incoming=True, func=lambda e: "t.me/" in e.text))
async def handler(event):
    status = await event.reply("📂 **ሊንኩን በማረጋገጥ ላይ...**")
    try:
        # ሊንኩን መተንተን (Link Parsing)
        link = event.text.split('/')
        msg_id = int(link[-1])
        
        # Private (c/...) እና Public ሊንኮችን መለየት
        if "/c/" in event.text:
            chat = int("-100" + link[-2])
        else:
            chat = link[-2]

        # ሜሴጁን ማግኘት
        target_msg = await client.get_messages(chat, ids=msg_id)

        if target_msg and target_msg.media:
            # ኦሪጅናል ስሙን መጠበቅ
            name = target_msg.file.name or "file.mp4"
            
            # --- FAST DOWNLOAD ---
            await status.edit(f"📥 **ማውረድ ተጀመረ:** `{name}`")
            path = await client.download_media(
                target_msg,
                progress_callback=lambda c, t: progress_bar(c, t, status, "Downloading")
            )
            
            # --- FAST UPLOAD ---
            await status.edit(f"📤 **መላክ ተጀመረ:** `{name}`")
            await client.send_file(
                'me', 
                path, 
                force_document=True, # ኦሪጅናል ፎርማቱን እንዲጠብቅ
                file_name=name,      # ኦሪጅናል ስሙን እንዲጠብቅ
                caption=f"✅ **ተጠናቀቀ:** `{name}`",
                progress_callback=lambda c, t: progress_bar(c, t, status, "Uploading")
            )
            
            # ሰርቨሩ እንዳይሞላ ፋይሉን ማጥፋት
            if os.path.exists(path): os.remove(path)
            await status.delete()
        else:
            await status.edit("❌ በዚህ ሊንክ ላይ ፋይል አልተገኘም!")

    except Exception as e:
        await status.edit(f"❌ ስህተት ተፈጥሯል: {str(e)}")

# --- 5. EXECUTION ---
if __name__ == "__main__":
    # ዌብ ሰርቨሩን ማስጀመር (ለ Render)
    Thread(target=run_flask).start()
    
    print("ቦቱ ስራ ጀምሯል... ሊንክ ለራስህ ላክ!")
    client.start()
    client.run_until_disconnected()
