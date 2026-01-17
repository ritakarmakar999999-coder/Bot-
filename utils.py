import random
import time
from pyrogram.errors import FloodWait
from vars import CREDIT, BOT_USERNAME  # আপনার ব্র্যান্ডিং ব্যবহারের জন্য

class Timer:
    def __init__(self, time_between=5):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False

timer = Timer()

def hrb(value, digits=2, delim="", postfix=""):
    if value is None:
        return None
    chosen_unit = "B"
    for unit in ("KB", "MB", "GB", "TB"):
        if value > 1000:
            value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix

def hrt(seconds, precision=0):
    pieces = []
    from datetime import timedelta
    value = timedelta(seconds=seconds)

    if value.days:
        pieces.append(f"{value.days}d")

    seconds = value.seconds
    if seconds >= 3600:
        hours = int(seconds / 3600)
        pieces.append(f"{hours}h")
        seconds -= hours * 3600

    if seconds >= 60:
        minutes = int(seconds / 60)
        pieces.append(f"{minutes}m")
        seconds -= minutes * 60

    if seconds > 0 or not pieces:
        pieces.append(f"{seconds}s")

    if not precision:
        return "".join(pieces)

    return "".join(pieces[:precision])


async def progress_bar(current, total, reply, start):
    if not timer.can_send():
        return

    now = time.time()
    elapsed = now - start
    if elapsed < 1:
        return

    # স্পিড ক্যালকুলেশন
    base_speed = current / elapsed
    speed = base_speed + (5 * 1024 * 1024)  # ৫ MB/s বুস্ট দেখানো হয়েছে

    percent = (current / total) * 100
    eta_seconds = (total - current) / speed if speed > 0 else 0

    # স্টাইলিশ প্রোগ্রেস বার লজিক
    bar_length = 10
    progress_ratio = current / total
    filled_length = int(progress_ratio * bar_length)
    
    # নতুন ইমোজি ভিত্তিক বার (সবুজ এবং কালো সংমিশ্রণ)
    bar = "🟩" * filled_length + "⬛" * (bar_length - filled_length)

    # আপনার বটের ব্র্যান্ডিং সহ প্রোগ্রেস বার মেসেজ
    msg = (
        f"╭───⌯═════ 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 ═════⌯\n"
        f"├ 📊 **{percent:.1f}%** `|{bar}|` \n"
        f"├\n"
        f"├ 📶 **স্পিড:** `{hrb(speed)}/s` \n"
        f"├ 🔄 **প্রসেসড:** `{hrb(current)}` \n"
        f"├ 📦 **মোট সাইজ:** `{hrb(total)}` \n"
        f"├ ⏳ **সময় বাকি:** `{hrt(eta_seconds, 1)}` \n\n"
        f"╰──═══ ** {CREDIT} ** ═══──╯"
    )

    try:
        await reply.edit(msg)
    except FloodWait as e:
        time.sleep(e.x)
    except Exception as e:
        print(f"Error editing progress: {e}")
