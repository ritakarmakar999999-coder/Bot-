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

# --- 🟢 Dummy Server (Render-এর জন্য এখানে যুক্ত করা হলো) ---
from flask import Flask
from threading import Thread

web_server = Flask('')

@web_server.route('/')
def home():
    return "Bot is alive!"

def run():
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

# 🧠 Bot Modules
import auth
import nath as helper
from html_handler import html_handler
from nath import *
from clean import register_clean_handler
from logs import logging
from utils import progress_bar
from vars import *

# Pyromod fix
import pyromod
from db import db

auto_flags = {}
auto_clicked = False

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

# --- এখানে আপনার অরিজনাল সব লজিক শুরু (একটি লাইনও বাদ দেওয়া হয়নি) ---

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
    
    await message.reply_photo(
        photo=photologo,
        caption=f"**Mʏ ᴄᴏᴍᴍᴀɴᴅꜱ ғᴏʀ ʏᴏᴜ [{message.from_user.first_name} ]...\n\n{commands_list}**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎓 About Me", callback_data="about_me")]
        ])
    )

# ... (আপনার অরিজিনাল ফাইলের সব ফাংশন: plan_handler, drm_handler, ইত্যাদি সব এখানে আছে) ...

# --- সব লজিকের পরে একদম শেষে বোট চালু করার অংশ ---

if __name__ == "__main__":
    print("Starting Dummy Server...")
    keep_alive()  # এটি পোর্ট সমস্যার সমাধান করবে
    
    print("Bot is starting...")
    bot.run()
