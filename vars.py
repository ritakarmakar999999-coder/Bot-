import os
from os import getenv

# 🔐 API & Bot Credentials
API_ID = int(getenv("API_ID", "0")) 
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")

# 🤖 Bot Username
BOT_USERNAME = getenv("BOT_USERNAME", "MyMyMyMyisnothingbhaibot")

# 🗄️ Database URL
MONGO_URL = getenv("MONGO_URL", "")

# 👤 Admin & Sudo Users
OWNER_ID = int(getenv("OWNER_ID", "")) 

# 🖼️ Logos & Pics (আপনার ছবি না থাকলেও এই লিঙ্কগুলো দরকার)
START_PIC = getenv("START_PIC", "https://telegra.ph/file/default.jpg")
photologo = getenv("photologo", "https://telegra.ph/file/default.jpg")

# 💳 Credit & Extra (লগের 'CREDIT' এরর ফিক্স করার জন্য)
CREDIT = getenv("CREDIT", "Nath") # এটি যুক্ত করা হয়েছে এরর ফিক্স করতে
LOG_GROUP = int(getenv("LOG_GROUP", "0"))
