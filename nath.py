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
from vars import * # আপনার vars.py থেকে OWNER_ID, BOT_USERNAME এবং CREDIT আসবে
from db import Database

# ভিডিওর ডিউরেশন বের করার ফাংশন
def get_duration(filename):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

# ২ জিবির চেয়ে বড় ভিডিও স্বয়ংক্রিয়ভাবে ভাগ করার ফাংশন
def split_large_video(file_path, max_size_mb=1900):
    size_bytes = os.path.getsize(file_path)
    max_bytes = max_size_mb * 1024 * 1024

    if size_bytes <= max_bytes:
        return [file_path] 

    duration = get_duration(file_path)
    parts = ceil(size_bytes / max_bytes)
    part_duration = duration / parts
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
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

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
        if thumb in ["/d", "no"] or not os.path.exists(thumb):
            temp_thumb = f"downloads/thumb_{os.path.basename(filename)}.jpg"
            
            # ভিডিওর ১০ সেকেন্ড থেকে থাম্বনেইল তৈরি
            subprocess.run(
                f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 -q:v 2 -y "{temp_thumb}"',
                shell=True
            )

            # থাম্বনেইলে ওয়াটারমার্ক বসানো (আপনার বটের ইউজারনেম)
            if os.path.exists(temp_thumb) and (watermark and watermark.strip() != "/d"):
                text_to_draw = watermark.strip()
                try:
                    probe_out = subprocess.check_output(
                        f'ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0:s=x "{temp_thumb}"',
                        shell=True,
                        stderr=subprocess.DEVNULL,
                    ).decode().strip()
                    img_width = int(probe_out.split('x')[0]) if 'x' in probe_out else int(probe_out)
                except Exception:
                    img_width = 1280

                font_size = max(32, int(img_width * 0.05))
                box_h = max(60, int(font_size * 1.6))
                safe_text = text_to_draw.replace("'", "\\'")

                text_cmd = (
                    f'ffmpeg -i "{temp_thumb}" -vf '
                    f'"drawbox=y=0:color=black@0.45:width=iw:height={box_h}:t=fill,'
                    f'drawtext=fontfile=font.ttf:text=\'{safe_text}\':fontcolor=white:'
                    f'fontsize={font_size}:x=(w-text_w)/2:y=(({box_h})-text_h)/2" '
                    f'-c:v mjpeg -q:v 2 -y "{temp_thumb}"'
                )
                subprocess.run(text_cmd, shell=True)
            
            thumbnail = temp_thumb if os.path.exists(temp_thumb) else None

        await prog.delete(True) 

        # আপলোডিং স্ট্যাটাস (বাংলায়)
        reply1 = await bot.send_message(channel_id, f"📥 **ভিডিও আপলোড হচ্ছে:**\n<blockquote>{name}</blockquote>")
        reply = await m.reply_text(f"🖼 **থাম্বনেইল জেনারেট হচ্ছে:**\n<blockquote>{name}</blockquote>")

        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        sent_message = None

        if file_size_mb < 2000:
            # ছোট ভিডিও সরাসরি আপলোড
            dur = int(duration(filename))
            start_time = time.time()

            try:
                sent_message = await bot.send_video(
                    chat_id=channel_id,
                    video=filename,
                    caption=cc,
                    supports_streaming=True,
                    height=720,
                    width=1280,
                    thumb=thumbnail,
                    duration=dur,
                    progress=progress_bar,
                    progress_args=(reply, start_time)
                )
            except Exception:
                sent_message = await bot.send_document(
                    chat_id=channel_id,
                    document=filename,
                    caption=cc,
                    progress=progress_bar,
                    progress_args=(reply, start_time)
                )

            if os.path.exists(filename):
                os.remove(filename)
            await reply.delete(True)
            await reply1.delete(True)

        else:
            # ২ জিবির বড় ভিডিও হলে স্প্লিট করা (বাংলা নোটিফিকেশন)
            notify_split = await m.reply_text(
                f"⚠️ ভিডিওটি ২ জিবির বেশি ({human_readable_size(os.path.getsize(filename))})\n"
                f"⏳ এটি পার্ট করে আপলোড করা হচ্ছে, দয়া করে অপেক্ষা করুন..."
            )

            parts = split_large_video(filename)

            try:
                first_part_message = None
                for idx, part in enumerate(parts):
                    part_dur = int(duration(part))
                    part_num = idx + 1
                    total_parts = len(parts)
                    part_caption = f"{cc}\n\n📦 **Part {part_num} of {total_parts}**\n🌟 {BOT_USERNAME}"
                    
                    upload_msg = await m.reply_text(f"📤 পার্ট {part_num}/{total_parts} আপলোড হচ্ছে...")

                    msg_obj = await bot.send_video(
                        chat_id=channel_id,
                        video=part,
                        caption=part_caption,
                        supports_streaming=True,
                        thumb=thumbnail,
                        duration=part_dur,
                        progress=progress_bar,
                        progress_args=(upload_msg, time.time())
                    )
                    if first_part_message is None:
                        first_part_message = msg_obj

                    await upload_msg.delete(True)
                    if os.path.exists(part):
                        os.remove(part)

                await notify_split.edit_text("✅ বড় ভিডিওটি সফলভাবে সবকটি পার্টে আপলোড হয়েছে!")

            except Exception as e:
                raise Exception(f"Upload failed at part {idx + 1}: {str(e)}")

            await reply.delete(True)
            await reply1.delete(True)
            if os.path.exists(filename):
                os.remove(filename)

            sent_message = first_part_message

        # থাম্বনেইল ক্লিনআপ
        if thumb in ["/d", "no"] and temp_thumb and os.path.exists(temp_thumb):
            os.remove(temp_thumb)

        return sent_message

    except Exception as err:
        raise Exception(f"send_vid failed: {err}")

# অন্যান্য প্রয়োজনীয় সাহায্যকারী ফাংশন (আগের মতোই রাখা হয়েছে)
def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

async def download_video(url, cmd, name):
    download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
    k = subprocess.run(download_cmd, shell=True)
    if os.path.isfile(f"{name}.mp4"):
        return f"{name}.mp4"
    return name + ".mp4"
