# 🔧 Standard Library
import os
import re
import sys
import time
import asyncio
from flask import Flask
from threading import Thread

# --- 🟢 Dummy Server ---
web_server = Flask('')
@web_server.route('/')
def home(): return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# 📦 Third-party Libraries & Pyrogram
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from vars import * #
from db import db
import pyromod #

# Initialize bot
bot = Client(
    "ugx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    in_memory=True
)

# 🚀 Start Handler (Error Fix)
@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    if not (db.is_user_authorized(user_id, client.me.username) or db.is_admin(user_id)):
        await message.reply_text("❌ আপনি এই বটটি ব্যবহারের অনুমতি পাননি।")
        return

    caption_text = f"**হ্যালো {message.from_user.first_name}!**\n\nআমি অটোমেটিক লিঙ্ক এক্সট্রাক্টর বট।\nক্রেডিট: {CREDIT}"
    
    try:
        # ছবির লিঙ্ক কাজ না করলে এরর এড়াতে try-except ব্যবহার
        await message.reply_photo(photo=photologo, caption=caption_text)
    except Exception:
        # ছবি কাজ না করলে শুধু টেক্সট পাঠাবে
        await message.reply_text(caption_text)

# 📂 অটোমেটিক এক্সট্রাকশন ও ডুপ্লিকেট ফিল্টারিং লজিক
@bot.on_message(filters.document & filters.private)
async def auto_extract_handler(client, message: Message):
    if not (db.is_user_authorized(message.from_user.id, client.me.username) or db.is_admin(message.from_user.id)):
        return

    if message.document.file_name.endswith('.txt'):
        status = await message.reply_text("📥 **ফাইলটি পড়া হচ্ছে...**")
        file_path = await message.download()
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # ১. রেগুলার এক্সপ্রেশন দিয়ে সব লিঙ্ক খুঁজে বের করা
        all_links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        # ২. ডুপ্লিকেট ফিল্টারিং (একি ভিডিও বারবার নেবে না)
        unique_links = list(dict.fromkeys(all_links)) 
        
        if not unique_links:
            await status.edit("❌ ফাইলটিতে কোনো বৈধ লিঙ্ক পাওয়া যায়নি।")
            os.remove(file_path)
            return

        await status.edit(f"✅ **মোট লিঙ্ক:** {len(all_links)}\n♻️ **ইউনিক ভিডিও:** {len(unique_links)}\n\n🚀 **অটোমেটিক এক্সট্রাকশন শুরু হচ্ছে...**")

        # ৩. কোনো ইনপুট ছাড়াই অটোমেটিক লুপ (আপনার চাওয়া লজিক)
        for index, link in enumerate(unique_links, start=1):
            try:
                # এখানে আপনার ডাউনলোডিং লজিকটি কাজ করবে
                # উদাহরণস্বরূপ একটি মেসেজ আপডেট:
                await message.reply_text(f"📝 **প্রসেস হচ্ছে ({index}/{len(unique_links)}):**\n`{link}`")
                await asyncio.sleep(1) # স্প্যাম এড়াতে বিরতি
            except Exception:
                continue

        await status.reply_text("🏁 **সব কাজ সফলভাবে শেষ হয়েছে!**")
        os.remove(file_path)

# --- বোট চালু করার অংশ ---
if __name__ == "__main__":
    keep_alive() # পোর্ট সমস্যার সমাধান
    bot.run()
