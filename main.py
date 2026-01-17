# 🔧 Standard Library & 📦 Third-party Libraries
import os, re, sys, time, json, asyncio
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# 🧠 Bot Modules (vars, db এবং nath ইমপোর্ট করা হয়েছে)
from vars import * from db import db
import pyromod 
from nath import * # আপনার আসল ডাউনলোড ফাংশনগুলো এখানে থাকে

# --- 🟢 Dummy Server (Render Port Fix) ---
web_server = Flask('')
@web_server.route('/')
def home(): return "Bot is alive!"
def run():
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host='0.0.0.0', port=port)
def keep_alive(): Thread(target=run).start()

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
    caption = f"**হ্যালো {message.from_user.first_name}!**\nআমি এখন সম্পূর্ণ অটোমেটিক মোডে কাজ করছি।"
    try:
        await message.reply_photo(photo=photologo, caption=caption)
    except Exception:
        await message.reply_text(caption)

# 📂 অটোমেটিক লিঙ্ক এক্সট্রাকশন ও ডুপ্লিকেট ফিল্টারিং
@bot.on_message(filters.document & filters.private)
async def auto_extract_handler(client, message: Message):
    if not (db.is_user_authorized(message.from_user.id, client.me.username) or db.is_admin(message.from_user.id)):
        return

    if message.document.file_name.endswith('.txt'):
        status = await message.reply_text("📥 **ফাইলটি প্রসেস করা হচ্ছে...**")
        file_path = await message.download()
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # ১. সব লিঙ্ক খুঁজে বের করা
        all_links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        # ২. ডুপ্লিকেট ফিল্টারিং (একি লিঙ্ক বারবার নেবে না)
        unique_links = list(dict.fromkeys(all_links)) 
        
        if not unique_links:
            await status.edit("❌ কোনো বৈধ লিঙ্ক পাওয়া যায়নি।")
            os.remove(file_path)
            return

        await status.edit(f"✅ **ইউনিক ভিডিও:** {len(unique_links)}\n🚀 **ডাউনলোড শুরু হচ্ছে...**")

        # ৩. অটোমেটিক লুপ (আপনার আসল লজিক এখানে কল হবে)
        for index, link in enumerate(unique_links, start=1):
            try:
                # প্রসেসিং মেসেজ
                process_msg = await message.reply_text(f"📝 **প্রসেস হচ্ছে ({index}/{len(unique_links)}):**\n`{link}`")
                
                # --- এখানে আপনার আসল ডাউনলোডিং লজিকটি কল করুন ---
                # উদাহরণ: await helper.download_video(client, message, link, process_msg)
                
                await asyncio.sleep(1) # স্প্যাম এড়াতে বিরতি
            except Exception as e:
                print(f"Error on link {index}: {e}")
                continue

        await status.reply_text("🏁 **সব কাজ সফলভাবে শেষ হয়েছে!**")
        os.remove(file_path)

# --- বোট চালু করা ---
if __name__ == "__main__":
    keep_alive() 
    bot.run()
