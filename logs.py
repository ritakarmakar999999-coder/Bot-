# logs.py

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from vars import BOT_USERNAME  # আপনার বটের নাম ব্যবহারের জন্য

# লগিং সেটআপ
logging.basicConfig(
    level=logging.INFO, # ERROR এর বদলে INFO দিলে বটের স্ট্যাটাস ভালো বোঝা যাবে
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("logs.txt", maxBytes=50000000, backupCount=10),
        logging.StreamHandler(),
    ],
)

# Pyrogram এর অতিরিক্ত লগ কমানো
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# লগার ইনিশিয়ালাইজ করা
logger = logging.getLogger()

# আপনার বটের জন্য কাস্টম স্টার্টআপ মেসেজ
logger.info(f"🚀 {BOT_USERNAME} - লগার সফলভাবে চালু হয়েছে!") #
logger.info("🛠️ আপনার প্রাইভেট সার্ভার এখন সক্রিয়।")
