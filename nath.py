import os
import re
import time
import mmap
import datetime
import aiohttp
import aiofiles
import asyncio
import logging
import requests
import tgcrypto
import subprocess
import concurrent.futures
from math import ceil
from utils import progress_bar
from pyrogram import Client, filters
from pyrogram.types import Message
from io import BytesIO
from pathlib import Path  
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import math
import m3u8
from urllib.parse import urljoin

# 🧠 মডিউল ইমপোর্ট ফিক্স
from vars import *
from db import Database

# ভিডিওর ডিউরেশন বের করার ফাংশন
def get_duration(filename):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return float(result.stdout.strip())
    except:
        return 0

# ২ জিবির চেয়ে বড় ভিডিও স্বয়ংক্রিয়ভাবে ভাগ করার ফাংশন
def split_large_video(file_path, max_size_mb=1900):
    size_bytes = os.path.getsize(file_path)
    max_bytes = max_size_mb * 1024 * 1024

    if size_bytes <= max_bytes:
        return [file_path] 

    duration_val = get_duration(file_path)
    parts = ceil(size_bytes / max_bytes)
    part_duration = duration_val / parts
    base_name = file_path.rsplit(".", 1)[0]
    output_files = []

    for i in range(parts):
        output_file = f"{base_name}_part{i+1}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", file_path,
            "-ss", str(int(part_duration * i)),
            "-t", str(int(part_duration)),
            "-c", "copy",
            output_file
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_file):
            output_files.append(output_file)

    return output_files

def duration(filename):
    return get_duration(filename)

async def aio(url,name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(k, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return k

# আপনার বটের ওয়াটারমার্ক সহ ভিডিও পাঠানোর প্রধান ফাংশন
async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog, channel_id, watermark=f"{BOT_USERNAME}", topic_thread_id: int = None):
    try:
        temp_thumb = None 
        thumbnail = thumb
        if thumb in ["/d", "no"] or not os.path.exists(str(thumb)):
            temp_thumb = f"thumb_{int(time.time())}.jpg"
            subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 -q:v 2 -y "{temp_thumb}"', shell=True)
            thumbnail = temp_thumb if os.path.exists(temp_thumb) else None

        # 🛠 সংশোধনী ১: প্রগ্রেস মেসেজ ডিলিট করার সময় এরর হ্যান্ডলিং
        if prog:
            try: await prog.delete()
            except: pass

        reply1 = await bot.send_message(channel_id, f"📥 **ভিডিও আপলোড হচ্ছে:**\n<blockquote>{name}</blockquote>")
        reply = await m.reply_text(f"🖼 **থাম্বনেইল জেনারেট হচ্ছে:**\n<blockquote>{name}</blockquote>")

        file_size_mb = os.path.getsize(filename) / (1024 * 1024)

        if file_size_mb < 2000:
            dur = int(duration(filename))
            start_time = time.time()
            try:
                await bot.send_video(
                    chat_id=channel_id,
                    video=filename,
                    caption=cc,
                    supports_streaming=True,
                    thumb=thumbnail,
                    duration=dur,
                    progress=progress_bar,
                    progress_args=(reply, start_time)
                )
            except Exception:
                await bot.send_document(chat_id=channel_id, document=filename, caption=cc)
            
            if os.path.exists(filename): os.remove(filename)
            await reply.delete()
            await reply1.delete()

        else:
            parts = split_large_video(filename)
            for idx, part in enumerate(parts):
                part_dur = int(duration(part))
                await bot.send_video(
                    chat_id=channel_id,
                    video=part,
                    caption=f"{cc}\n\n📦 Part {idx+1}",
                    supports_streaming=True,
                    thumb=thumbnail,
                    duration=part_dur
                )
                if os.path.exists(part): os.remove(part)
            
            await reply.delete()
            await reply1.delete()
            if os.path.exists(filename): os.remove(filename)

        if temp_thumb and os.path.exists(temp_thumb): os.remove(temp_thumb)
        return True

    except Exception as err:
        logging.error(f"send_vid failed: {err}")
        return False

# --- 🟢 আর্গুমেন্ট ফিক্সড করা হয়েছে ---
async def download_video(client: Client, message: Message, url, prog):
    name = f"vid_{int(time.time())}"
    filename = f"{name}.mp4"
    
    # 🛠 সংশোধনী ২: কমান্ড স্ট্রিং ফিক্স
    cmd = f'yt-dlp -o "{filename}" "{url}" -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
    
    await prog.edit(f"📥 **ডাউনলোড হচ্ছে...**\n`{url}`")
    
    # 🛠 সংশোধনী ৩: Subprocess এরর হ্যান্ডলিং
    try:
        subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        await prog.edit(f"❌ ডাউনলোড এরর: {e}")
        return None
    
    if os.path.exists(filename):
        caption = f"✅ **ফাইল:** `{name}`\n🌟 @{BOT_USERNAME}"
        # মেইন ফাইলের কল অনুযায়ী সঠিক চ্যাট আইডি পাঠানো হয়েছে
        await send_vid(client, message, caption, filename, "no", name, prog, message.chat.id)
        return filename
    return None
