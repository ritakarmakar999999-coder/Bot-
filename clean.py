import os
import glob
from pathlib import Path
from pyrogram import Client, filters
from vars import ADMINS, BOT_USERNAME  # vars.py থেকে প্রয়োজনীয় তথ্য আনা হয়েছে
from db import db
from datetime import datetime
from pyrogram.handlers import MessageHandler

def clean_downloads():
    """ডাউনলোড ডিরেক্টরি পুরোপুরি পরিষ্কার করার ফাংশন"""
    try:
        # ডাউনলোড ডিরেক্টরি না থাকলে তৈরি করা
        os.makedirs("downloads", exist_ok=True)
        
        # সব ফাইল রিমুভ করা
        for file in glob.glob("downloads/*"):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    print(f"Removed from downloads: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")
    except Exception as e:
        print(f"Error cleaning downloads: {e}")

def clean_media_files():
    """wm.png বাদে বাকি সব মিডিয়া ফাইল পরিষ্কার করা"""
    try:
        image_formats = ["*.jpg", "*.jpeg", "*.png"]
        video_formats = ["*.mp4", "*.mkv", "*.webm"]
        temp_formats = ["*.part", "*.ytdl"]
        
        formats_to_clean = image_formats + video_formats + temp_formats
        
        for format_pattern in formats_to_clean:
            for file in glob.glob(format_pattern):
                try:
                    # আপনার ওয়াটারমার্ক ফাইল wm.png এড়িয়ে যাওয়া
                    if file == "wm.png":
                        continue
                        
                    if os.path.isfile(file):
                        os.remove(file)
                        print(f"Removed from root: {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")
    except Exception as e:
        print(f"Error cleaning media files: {e}")

def clean_all():
    """সব ফাইল একসাথে পরিষ্কার করা"""
    clean_downloads()
    clean_media_files()

async def clean_expired_users(client: Client):
    """মেয়াদ শেষ হওয়া ইউজারদের ডাটাবেস থেকে রিমুভ করা"""
    try:
        bot_username = BOT_USERNAME
        users = db.list_users(bot_username)
        
        removed_count = 0
        now = datetime.now()
        
        for user in users:
            expiry = user['expiry_date']
            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
                
            if expiry <= now:
                # ইউজারকে বাংলা ভাষায় নোটিফিকেশন পাঠানো
                try:
                    await client.send_message(
                        user['user_id'],
                        f"**⚠️ আপনার মেম্বারশিপের মেয়াদ শেষ হয়েছে!**\n\n"
                        f"বটটি পুনরায় ব্যবহার করতে {BOT_USERNAME} এর অ্যাডমিনের সাথে যোগাযোগ করুন।"
                    )
                except Exception as e:
                    print(f"Failed to notify user {user['user_id']}: {e}")
                
                # ইউজার রিমুভ করা
                if db.remove_user(user['user_id'], bot_username):
                    removed_count += 1
                    
        return removed_count
        
    except Exception as e:
        print(f"Error cleaning expired users: {e}")
        return 0

# Command handler for /clean
async def handle_clean_command(client: Client, message):
    """/clean কমান্ড হ্যান্ডলার (শুধুমাত্র আপনার জন্য)"""
    try:
        # আপনার আইডি ADMINS লিস্টে আছে কি না চেক করা
        if message.from_user.id not in ADMINS:
            await message.reply_text("<b>❌ দুঃখিত, এই কমান্ডটি শুধুমাত্র অ্যাডমিনদের জন্য।</b>")
            return
            
        status_msg = await message.reply_text("🧹 সার্ভার এবং মেয়াদোত্তীর্ণ ডাটা পরিষ্কার করা হচ্ছে...")
        
        clean_all()
        removed_users = await clean_expired_users(client)
        
        # সফলতার স্ট্যাটাস মেসেজ
        await status_msg.edit_text(
            f"<b>✅ ক্লিনআপ সফলভাবে সম্পন্ন হয়েছে!</b>\n\n"
            f"📁 ডাউনলোড ফোল্ডার পরিষ্কার করা হয়েছে।\n"
            f"🎬 মিডিয়া ফাইল ডিলিট করা হয়েছে।\n"
            f"👤 <code>{removed_users}</code> জন ইউজারকে রিমুভ করা হয়েছে।"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ এরর: {str(e)}")

# হ্যান্ডলার রেজিস্টার করা
def register_clean_handler(bot: Client):
    bot.add_handler(MessageHandler(handle_clean_command, filters.command("clean") & filters.private))

# বট চালু হওয়ার সময় অটোমেটিক ক্লিন করা
clean_all()
