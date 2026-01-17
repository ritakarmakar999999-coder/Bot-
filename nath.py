import os
import re
import time
import subprocess
import logging
import asyncio
import aiohttp
from math import ceil
from pyrogram import Client
from pyrogram.types import Message
from utils import progress_bar 
from vars import *

# ১. ড্রিম কী এপিআই ফাংশন (নতুন যোগ করা হয়েছে)
async def get_keys_from_api(pssh, license_url):
    """এটি একটি ফ্রি API ব্যবহার করে অটোমেটিক কী খুঁজে আনার চেষ্টা করবে"""
    # এখানে আপনার আসল এপিআই লিঙ্কটি বসাবেন
    api_url = "https://keyserver.onrender.com/decrypt" 
    payload = {"pssh": pssh, "license_url": license_url}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("keys", "") 
    except Exception as e:
        logging.error(f"DRM API Error: {e}")
        return None

# ২. ফাস্টার ডিউরেশন চেক
def get_duration(filename):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=8
        )
        return float(result.stdout.strip())
    except Exception:
        return 0

# ৩. মাল্টি-থ্রেডেড ভিডিও স্প্লিটিং
def split_large_video(file_path, max_size_mb=1900):
    size_bytes = os.path.getsize(file_path)
    max_bytes = max_size_mb * 1024 * 1024
    if size_bytes <= max_bytes:
        return [file_path]

    duration_val = get_duration(file_path)
    if duration_val == 0: return [file_path]

    parts = ceil(size_bytes / max_bytes)
    part_duration = duration_val / parts
    base_name = file_path.rsplit(".", 1)[0]
    output_files = []

    for i in range(parts):
        output_file = f"{base_name}_part{i+1}.mp4"
        cmd = ["ffmpeg", "-y", "-i", file_path, "-ss", str(int(part_duration * i)), "-t", str(int(part_duration)), "-c", "copy", "-threads", "0", "-map", "0", output_file]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_file):
            output_files.append(output_file)
    return output_files

# ৪. হাই-স্পিড আপলোড
async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog, chat_id):
    try:
        temp_thumb = None
        if thumb in ["/d", "no"] or not os.path.exists(str(thumb)):
            temp_thumb = f"thumb_{int(time.time())}.jpg"
            subprocess.run(f'ffmpeg -ss 00:00:02 -i "{filename}" -vframes 1 -q:v 2 -y "{temp_thumb}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            thumbnail = temp_thumb if os.path.exists(temp_thumb) else None
        else:
            thumbnail = thumb

        reply = await bot.send_message(m.chat.id, f"⚡ **আপলোড হচ্ছে:** `{name}`")
        dur = int(get_duration(filename))
        start_time = time.time()

        await bot.send_video(
            chat_id=chat_id,
            video=filename,
            caption=cc,
            supports_streaming=True,
            thumb=thumbnail,
            duration=dur,
            progress=progress_bar,
            progress_args=(reply, start_time)
        )
        
        if os.path.exists(filename): os.remove(filename)
        if temp_thumb and os.path.exists(temp_thumb): os.remove(temp_thumb)
        try: await reply.delete()
        except: pass
        return True
    except Exception as e:
        logging.error(f"Upload Error: {e}")
        return False

# ৫. সুপার ফাস্ট ডাউনলোড (DRM Key Logic সহ)
async def download_video(client: Client, message: Message, url, prog):
    name = f"vid_{int(time.time())}"
    filename = f"{name}.mp4"
    
    # --- DRM Key Fetching Logic (এখানেই পরিবর্তন করা হয়েছে) ---
    # মনে করুন ইউজার লিঙ্কের সাথে PSSH এবং License দিয়েছে অথবা আপনার বট এটি অটো বের করবে
    pssh = "" # আপনার লজিক অনুযায়ী এখান PSSH দিতে হবে
    license_url = "" # লাইসেন্স ইউআরএল
    
    key_option = ""
    if "akamaized" in url or ".mpd" in url:
        await prog.edit("🔑 **অটোমেটিক DRM কী খোঁজা হচ্ছে...**")
        keys = await get_keys_from_api(pssh, license_url)
        if keys:
            key_option = f'--allow-unplayable-formats --remotely-decrypt-keys "{keys}"'
            await prog.edit("✅ **কী পাওয়া গেছে! ভিডিও আনলক হচ্ছে...**")
    
    cmd = (
        f'yt-dlp {key_option} -o "{filename}" "{url}" '
        f'--add-header "Authorization:Bearer {JWT_TOKEN}" '
        f'--add-header "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" '
        f'--concurrent-fragments 10 '
        f'--no-check-certificate '
        f'--fixup never'
    )
    # ---------------------------------------------------

    await prog.edit(f"🚀 **ডাউনলোড শুরু হচ্ছে...**")

    try:
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await process.communicate()
        
        if os.path.exists(filename):
            caption = f"✅ **ফাইল:** `{name}`\n🌟 @{BOT_USERNAME}"
            
            if os.path.getsize(filename) > 1900 * 1024 * 1024:
                parts = split_large_video(filename)
                for part in parts:
                    await send_vid(client, message, caption, part, "no", name, prog, message.chat.id)
                if os.path.exists(filename): os.remove(filename)
            else:
                await send_vid(client, message, caption, filename, "no", name, prog, message.chat.id)
            
            try: await prog.delete()
            except: pass
            return filename
    except Exception as e:
        await prog.edit(f"❌ **সিস্টেম এরর:** {e}")
    return None
