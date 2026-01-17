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

# --- 🟢 Dummy Server Start (Line 23) ---
from flask import Flask
from threading import Thread

web_server = Flask('')

@web_server.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render-এর জন্য ডাইনামিক পোর্ট নির্ধারণ
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
watermark = "/d"  # Default value
count = 0
userbot = None
timeout_duration = 300  # 5 minutes

# Initialize bot with random session
bot = Client(
    "ugx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    sleep_threshold=60,
    in_memory=True
)

# ... (আপনার ৯৭০+ লাইনের বাকি সব কোড এখানে থাকবে) ...
# ... (নিচের কমান্ডগুলো এবং ফাংশনগুলো আগের মতোই থাকবে) ...

# --- শেষের দিকের অংশ যেখানে বোট চালু হবে ---

if __name__ == "__main__":
    print("Starting Dummy Server...")
    keep_alive()  # এটি আপনার পোর্টের সমস্যা মিটিয়ে বোটকে রেসপন্ড করতে সাহায্য করবে
    
    print("Bot Started...")
    bot.run() # এটি বোটকে টেলিগ্রামের সাথে কানেক্ট করবে
