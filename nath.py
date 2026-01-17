import os
import re
import time
import subprocess
import logging
import asyncio
from math import ceil
from pyrogram import Client
from pyrogram.types import Message
from utils import progress_bar 
from vars import *

# ১. ফাস্টার ডিউরেশন চেক (Fast Scan)
def get_duration(filename):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=8
        )
        return float(result.stdout.strip())
    except Exception:
        return 0

# ২. মাল্টি-থ্রেডেড ভিডিও স্প্লিটিং (CPU Optimization)
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
        # threads 0 দিলে সার্ভারের সব CPU কোর ব্যবহার হবে
        cmd = ["ffmpeg", "-y", "-i", file_path, "-ss", str(int(part_duration * i)), "-t", str(int(part_duration)), "-c", "copy", "-threads", "0", "-map", "0", output_file]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_file):
            output_files.append(output_file)
    return output_files

# ৩. হাই-স্পিড আপলোড ও অটো-ফরওয়ার্ড
async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog, channel_id):
    try:
        temp_thumb = None
        if thumb in ["/d", "no"] or not os.path.exists(str(thumb)):
            temp_thumb = f"thumb_{int(time.time())}.jpg"
            subprocess.run(f'ffmpeg -ss 00:00:02 -i "{filename}" -vframes 1 -q:v 2 -y "{temp_thumb}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            thumbnail = temp_thumb if os.path.exists(temp_thumb) else None
        else:
            thumbnail = thumb

        reply = await bot.send_message(m.chat.id, f"⚡ **চ্যানেলে আপলোড হচ্ছে:** `{name}`")
        dur = int(get_duration(filename))
        start_time = time.time()

        # সরাসরি নির্ধারিত চ্যানেলে আপলোড
        sent_video = await bot.send_video(
            chat_id=channel_id,
            video=filename,
            caption=cc,
            supports_streaming=True,
            thumb=thumbnail,
            duration=dur,
            progress=progress_bar,
            progress_args=(reply, start_time)
        )
        
        # আপলোড শেষে ভিডিওটি ব্যবহারকারীর কাছে কপি পাঠানো
        await sent_video.copy(m.chat.id, caption=cc)

        if os.path.exists(filename): os.remove(filename)
        if temp_thumb and os.path.exists(temp_thumb): os.remove(temp_thumb)
        
        try: await reply.delete()
        except: pass
        return True
    except Exception as e:
        logging.error(f"Upload Error: {e}")
        return False

# ৪. সুপার ফাস্ট ডাউনলোড (Aria2c + yt-dlp)
async def download_video(client: Client, message: Message, url, prog):
    name = f"vid_{int(time.time())}"
    filename = f"{name}.mp4"
    
    cmd = (
        f'yt-dlp -o "{filename}" "{url}" '
        f'--concurrent-fragments 10 ' 
        f'--external-downloader aria2c '
        f'--downloader-args "aria2c: -x 16 -j 16 -s 16" '
        f'--no-check-certificate'
    )

    await prog.edit(f"🚀 **সুপার ফাস্ট ডাউনলোড হচ্ছে...**")

    try:
        process = await asyncio.create_subprocess_shell(
            cmd, 
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if os.path.exists(filename):
            caption = f"✅ **ফাইল:** `{name}`\n🌟 @{BOT_USERNAME}"
            target_chat = LOG_CHANNEL 

            if os.path.getsize(filename) > 1900 * 1024 * 1024:
                parts = split_large_video(filename)
                for part in parts:
                    await send_vid(client, message, caption, part, "no", name, prog, target_chat)
                if os.path.exists(filename): os.remove(filename)
            else:
                await send_vid(client, message, caption, filename, "no", name, prog, target_chat)
            
            try: await prog.delete()
            except: pass
            return filename
    except Exception as e:
        await prog.edit(f"❌ **সিস্টেম এরর:** {e}")
    return None
