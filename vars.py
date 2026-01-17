import os
from os import getenv

# 🔐 API & Bot Credentials (Render-এর Environment Variables থেকে আসবে)
API_ID = int(getenv("API_ID", "0")) 
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")

# 🤖 Bot Username (লগের ImportError ঠিক করার জন্য)
BOT_USERNAME = getenv("BOT_USERNAME", "MyMyMyMyisnothingbhaibot")

# 🗄️ Database URL
MONGO_URL = getenv("MONGO_URL", "")

# 👤 Admin & Sudo Users
OWNER_ID = int(getenv("OWNER_ID", "123456789")) 

# 🖼️ Logos & Pics (নতুন এরর 'photologo' ফিক্স করার জন্য)
# আপনার পছন্দের কোনো ছবির লিঙ্ক এখানে দিতে পারেন
START_PIC = getenv("START_PIC", "https://telegra.ph/file/default.jpg")
photologo = getenv("photologo", "https://telegra.ph/file/default.jpg")

# 📁 Extra Settings
LOG_GROUP = int(getenv("LOG_GROUP", "0"))
