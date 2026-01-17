import os
from os import getenv

# 🔐 API & Bot Credentials
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")

# 🤖 Bot Username
# এই ভেরিয়েবলটি আপনার বটের ইউজারনেম হিসেবে কাজ করবে
BOT_USERNAME = getenv("BOT_USERNAME", "MyMyMyisnothingbhaibot")

# 📢 Log Channel ID
# আপনার ভিডিওগুলো যেখানে আপলোড হবে সেই চ্যানেলের আইডি এখানে থাকবে
LOG_CHANNEL = int(getenv("LOG_CHANNEL", "-1000000000000"))

# 🗄️ Database URL
MONGO_URL = getenv("MONGO_URL", "")

# 👤 Admin & Sudo Users
OWNER_ID = int(getenv("OWNER_ID", "123456789")) # এখানে আপনার নিজের আইডি বসান
ADMINS = [OWNER_ID] # এই লাইনটি লগের 'ADMINS' এররটি ফিক্স করবে

# 🖼️ Logos & Pics
START_PIC = getenv("START_PIC", "https://telegra.ph/file/default.jpg")
photologo = getenv("photologo", "https://graph.org/file/f70445d06b6b72d80c653.jpg") 

# 💳 Credit & Extra
CREDIT = getenv("CREDIT", "Nath") 
LOG_GROUP = int(getenv("LOG_GROUP", "0"))
