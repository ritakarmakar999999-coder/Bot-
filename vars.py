import os
from os import environ

# 🛰️ API Configuration - Render-এর Environment থেকে আসবে
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# 🍃 MongoDB Configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
MONGO_URL = DATABASE_URL

# 👑 Owner and Admin Configuration
# আপনার টেলিগ্রাম আইডি Render-এ OWNER_ID হিসেবে দিতে হবে
OWNER_ID = int(os.environ.get("OWNER_ID"))
# অ্যাডমিন লিস্ট - ডিফল্ট হিসেবে মালিকের আইডি থাকবে
ADMINS = [int(x) for x in os.environ.get("ADMINS", str(OWNER_ID)).split()]

# 🌐 Web Server Configuration (Render-এর জন্য)
WEB_SERVER = os.environ.get("WEB_SERVER", "False").lower() == "true"
PORT = int(os.environ.get("PORT", 8080))

# 🏷️ Bot Branding
BOT_USERNAME = "@MyMyMyMyisnothingbhaibot"
CREDIT = "MyPrivateBot"

# 💬 Message Formats
AUTH_MESSAGES = {
    "subscription_active": "<b>✅ Subscription Activated!</b>",
    "subscription_expired": "<b>⚠️ Your Subscription Has Ended!</b>",
    "access_denied": "<b>❌ Access Denied!</b>"
}
