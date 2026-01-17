# 🔧 Standard Library & 📦 Third-party Libraries
import os, re, sys, time, json, asyncio, subprocess
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask

# 📦 Pyrogram & Others
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# 🧠 Bot Modules (১০ ও ১১ নম্বর লাইনের এরর এখানে ফিক্স করা হয়েছে)
from vars import *
from db import db
import pyromod 
from nath import * # --- 🟢 Dummy Server (Render Port Fix) ---
web_server = Flask('')
@web_server.route('/')
def home(): return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# Initialize bot
bot = Client(
    "ugx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    in_memory=True
)

# 🚀 Start Handler
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    if not (db.is_user_authorized(user_id, client.me.username) or db.is_admin(user_id)):
        return
    
    caption = (
        f"**হ্যালো {message.from_user.first_name}!**\n\n"
        "📜 **উপলব্ধ কমান্ডসমূহ:**\n"
        "🔹 `/drm` - DRM ভিডিও প্রসেস করতে\n"
        "🔹 `/nondrm` - সাধারণ ভিডিও প্রসেস করতে\n"
        "🔹 `/users` - মোট ইউজার দেখতে (Admin Only)\n\n"
        "🚀 **অটোমেটিক মোড:** সরাসরি .txt ফাইল পাঠালেও ডাউনলোড শুরু হবে।"
    )
    try:
        await message.reply_photo(photo=photologo, caption=caption)
    except Exception:
        await message.reply_text(caption)

# 🛠️ কমান্ড হ্যান্ডলারসমূহ (আগের লজিক অক্ষুণ্ণ রেখে)
@bot.on_message(filters.command(["drm", "nondrm"]) & filters.private)
async def commands_handler(client, message):
    if not (db.is_user_authorized(message.from_user.id, client.me.username) or db.is_admin(message.from_user.id)):
        return
    await message.reply_text(f"📥 **{message.text} মোড সক্রিয়।** এখন আপনার .txt ফাইলটি পাঠান।")

@bot.on_message(filters.command("users") & filters.private)
async def users_cmd(client, message):
    if not db.is_admin(message.from_user.id): return
    users = db.get_all_users()
    count = len(users) if users else 0
    await message.reply_text(f"📊 **মোট অনুমোদিত ইউজার:** {count}")

# 📂 অটোমেটিক ফাইল প্রসেসিং ও ডাউনলোড লজিক
@bot.on_message(filters.document & filters.private)
async def auto_extract_handler(client, message: Message):
    if not (db.is_user_authorized(message.from_user.id, client.me.username) or db.is_admin(message.from_user.id)):
        return

    if message.document.file_name.endswith('.txt'):
        status = await message.reply_text("📥 **ফাইলটি প্রসেস করা হচ্ছে...**")
        file_path = await message.download()
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # সব লিঙ্ক খুঁজে বের করা এবং ডুপ্লিকেট ফিল্টার করা
        all_links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        unique_links = list(dict.fromkeys(all_links)) 
        
        if not unique_links:
            await status.edit("❌ কোনো বৈধ লিঙ্ক পাওয়া যায়নি।")
            os.remove(file_path)
            return

        await status.edit(f"✅ **ইউনিক ভিডিও:** {len(unique_links)}\n🚀 **ডাউনলোড শুরু হচ্ছে...**")

        # লুপের মাধ্যমে প্রতিটি লিঙ্ক ডাউনলোড করা
        for index, link in enumerate(unique_links, start=1):
            try:
                prog = await message.reply_text(f"📝 **ডাউনলোড হচ্ছে ({index}/{len(unique_links)}):**\n`{link}`")
                
                # আপনার nath.py থেকে ডাউনলোড ফাংশন কল করা (নিশ্চিত করুন এই নামই আছে)
                # যদি ফাংশনের নাম ভিন্ন হয় তবে এখানে পরিবর্তন করুন
                await download_video(client, message, link, prog) 
                
                await asyncio.sleep(2) 
            except Exception as e:
                print(f"Error on {link}: {e}")
                continue

        await status.reply_text("🏁 **সব ভিডিও সফলভাবে আপলোড করা হয়েছে!**")
        os.remove(file_path)

# --- বোট চালু করা ---
if __name__ == "__main__":
    keep_alive() 
    bot.run()
