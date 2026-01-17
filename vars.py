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
OWNER_ID = int(getenv("OWNER_ID", "123456789")) 
ADMINS = [OWNER_ID] # এই লাইনটি 'ADMINS' এরর ফিক্স করবে

# 🖼️ Logos & Pics
START_PIC = getenv("START_PIC", "https://telegra.ph/file/default.jpg")
photologo = getenv("photologo", "https://telegra.ph/file/default.jpg")

# 💳 Credit & Extra
CREDIT = getenv("CREDIT", "Nath")
LOG_GROUP = int(getenv("LOG_GROUP", "0"))
