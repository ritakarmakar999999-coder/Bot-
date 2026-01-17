# 🔧 Standard Library
import os
import re
import sys
import time
import json
import random
import string
import shutil
import zipfile
import urllib
import subprocess
from datetime import datetime, timedelta
from base64 import b64encode, b64decode
from subprocess import getstatusoutput

# 🕒 Timezone
import pytz

# --- 🟢 Dummy Server (Render-এর জন্য) ---
from flask import Flask
from threading import Thread

web_server = Flask('')

@web_server.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render-এর পোর্ট সমস্যার সমাধান করবে এই অংশটি
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# --- Dummy Server End ---

# 📦 Third-party Libraries
import aiohttp
import aiofiles
import requests
import asyncio
import ffmpeg
import m3u8
import cloudscraper
import yt_dlp
import tgcrypto
from logs import logging
from bs4 import BeautifulSoup
from pytube import YouTube
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ⚙️ Pyrogram
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
from pyrogram.errors import (
    FloodWait,
    BadRequest,
    Unauthorized,
    SessionExpired,
    AuthKeyDuplicated,
    AuthKeyUnregistered,
    ChatAdminRequired,
    PeerIdInvalid,
    RPCError
)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

# 🧠 Bot Modules (vars থেকে সব ইমপোর্ট করা হয়েছে এরর এড়াতে)
import auth
import nath as helper
from html_handler import html_handler
from nath import *
from clean import register_clean_handler
from logs import logging
from utils import progress_bar
from vars import * #

# Pyromod fix
import pyromod
from db import db

# Global variables
watermark = "/d"  
count = 0
userbot = None
timeout_duration = 300  

# Initialize bot
bot = Client(
    "ugx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    sleep_threshold=60,
    in_memory=True
)

# --- লজিক সেকশন ---

@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user_id = message.from_user.id
    is_authorized = db.is_user_authorized(user_id, client.me.username)
    is_admin = db.is_admin(user_id)
    
    if not is_authorized and not is_admin:
        await message.reply_text(f"**ʜᴇʟʟᴏ {message.from_user.first_name}**\n\n**ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴍᴇ. ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇꜱꜱ.**")
        return

    commands_list = (
        "**>  /drm - ꜱᴛᴀʀᴛ ᴜᴘʟᴏᴀᴅɪɴɢ ᴄᴘ/ᴄᴡ ᴄᴏᴜʀꜱᴇꜱ**\n"
        "**>  /plan - ᴠɪᴇᴡ ʏᴏᴜʀ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ ᴅᴇᴛᴀɪʟꜱ**\n"
    )
    
    if is_admin:
        commands_list += (
            "\n**👑 Admin Commands**\n"
            "• /users - List all users\n"
        )
    
    # photologo ভেরিয়েবলটি vars.py থেকে আসছে
    await message.reply_photo(
        photo=photologo,
        caption=f"**Mʏ ᴄᴏᴍᴍᴀɴᴅꜱ ғᴏʀ ʏᴏᴜ [{message.from_user.first_name} ]...\n\n{commands_list}**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎓 About Me", callback_data="about_me")]
        ])
    )

# --- নতুন অটোমেটিক এক্সট্রাকশন ও ডুপ্লিকেট ফিল্টারিং লজিক ---

@bot.on_message(filters.document & filters.private)
async def auto_extract_handler(client, message: Message):
    # আপনার অনুমোদিত ইউজার চেক
    user_id = message.from_user.id
    if not (db.is_user_authorized(user_id, client.me.username) or db.is_admin(user_id)):
        return

    if message.document.file_name.endswith('.txt'):
        msg = await message.reply_text("📥 **ফাইলটি প্রসেস করা হচ্ছে...**")
        file_path = await message.download()
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # ১. সব লিঙ্ক খুঁজে বের করা
        all_links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        # ২. ডুপ্লিকেট ফিল্টারিং (একি ভিডিও বারবার নেবে না)
        unique_links = list(dict.fromkeys(all_links)) 
        
        if not unique_links:
            await msg.edit("❌ **ফাইলটিতে কোনো বৈধ লিঙ্ক পাওয়া যায়নি।**")
            os.remove(file_path)
            return

        await msg.edit(
            f"✅ **মোট লিঙ্ক:** {len(all_links)}\n"
            f"♻️ **ইউনিক ভিডিও:** {len(unique_links)}\n\n"
            "🚀 **অটোমেটিক এক্সট্রাকশন শুরু হচ্ছে...**"
        )

        # ৩. কোনো ইনপুট ছাড়াই অটোমেটিক লুপ
        for index, link in enumerate(unique_links, start=1):
            try:
                # আপনার অরিজিনাল এক্সট্রাকশন ফাংশন (drm_handler এর ভেতরের লজিক) এখানে কাজ করবে
                # এখানে শুধু উদাহরণ হিসেবে মেসেজ দেওয়া হলো
                await message.reply_text(f"📝 **প্রসেস হচ্ছে ({index}/{len(unique_links)}):**\n`{link}`")
                await asyncio.sleep(1) # স্প্যাম এড়াতে
            except Exception as e:
                logging.error(f"Error on link {index}: {e}")
                continue

        await msg.reply_text("🏁 **সব কাজ সফলভাবে শেষ হয়েছে!**")
        os.remove(file_path)

# --- বোট চালু করার অংশ ---

if __name__ == "__main__":
    print("Starting Dummy Server...")
    keep_alive() 
    
    print("Bot is starting...")
    bot.run()
