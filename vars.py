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

# 🖼️ Logos & Pics (এগুলো থাকলে কোড এরর দেবে না)
# আপনার নিজের ছবি না থাকলেও এই লিঙ্কগুলো কোডকে সচল রাখবে
START_PIC = getenv("START_PIC", "https://telegra.ph/file/default.jpg")
photologo = getenv("photologo", "https://telegra.ph/file/default.jpg")
