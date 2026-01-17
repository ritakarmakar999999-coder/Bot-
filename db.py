import os
import time
import certifi
import colorama
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
from pymongo import MongoClient, errors
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection
from colorama import Fore, Style
from vars import *

# 🌍 Load Environment Variables
MONGO_URL = os.environ.get("MONGO_URL")
if not MONGO_URL:
    raise ValueError("❌ MONGO_URL not found in Render Environment Variables!")

class Database:
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        """Initialize MongoDB connection with retry logic"""
        self._print_startup_message()
        self.client: Optional[MongoClient] = None
        self.db: Optional[MongoDatabase] = None
        self.users: Optional[Collection] = None
        self.settings: Optional[Collection] = None
        self._connect_with_retry(max_retries, retry_delay)
        
    def _connect_with_retry(self, max_retries: int, retry_delay: float):
        for attempt in range(1, max_retries + 1):
            try:
                print(f"{Fore.YELLOW}⌛ Attempt {attempt}/{max_retries}: Connecting to MongoDB...{Style.RESET_ALL}")
                
                self.client = MongoClient(
                    MONGO_URL,
                    serverSelectionTimeoutMS=20000,
                    tlsCAFile=certifi.where(),
                    retryWrites=True
                )
                
                self.client.server_info()
                # 🛠️ আপনার নিজস্ব ডাটাবেস নাম
                self.db = self.client.get_database('My_Private_Bot_DB')
                self.users = self.db['users']
                self.settings = self.db['user_settings']
                
                print(f"{Fore.GREEN}✓ MongoDB Connected Successfully!{Style.RESET_ALL}")
                self._initialize_database()
                return
                
            except Exception as e:
                print(f"{Fore.RED}✕ Connection attempt {attempt} failed: {str(e)}{Style.RESET_ALL}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(f"Failed to connect after {max_retries} attempts")

    def _print_startup_message(self):
        # 🛡️ এখানে আপনার নতুন বটের নাম সেট করা হয়েছে
        bot_display_name = "@MyMyMyMyisnothingbhaibot"
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"🚀 {bot_display_name} - Database Initialization")
        print(f"{'='*50}{Style.RESET_ALL}\n")

    def _initialize_database(self):
        try:
            self.users.create_index([("bot_username", 1), ("user_id", 1)], unique=True)
            self.settings.create_index([("user_id", 1)], unique=True)
        except: pass

    def is_user_authorized(self, user_id: int, bot_username: str = "@MyMyMyMyisnothingbhaibot") -> bool:
        """Check user authorization status"""
        # 👑 OWNER_ID এবং ADMINS (vars.py থেকে) থাকলে সরাসরি এক্সেস পাবে
        if user_id == OWNER_ID or user_id in ADMINS:
            return True
        user = self.users.find_one({"user_id": user_id, "bot_username": bot_username})
        if not user or 'expiry_date' not in user:
            return False
        
        expiry = user['expiry_date']
        if isinstance(expiry, str):
            try:
                expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
            except: return False
        return expiry > datetime.now()

    def add_user(self, user_id: int, name: str, days: int, bot_username: str = "@MyMyMyMyisnothingbhaibot"):
        """Add or update a user"""
        expiry_date = datetime.now() + timedelta(days=days)
        self.users.update_one(
            {"user_id": user_id, "bot_username": bot_username},
            {"$set": {"name": name, "expiry_date": expiry_date, "added_date": datetime.now()}},
            upsert=True
        )
        return True, expiry_date

    def list_users(self, bot_username: str = "@MyMyMyMyisnothingbhaibot"):
        """List all users for the bot"""
        return list(self.users.find({"bot_username": bot_username}))

    def get_user_expiry_info(self, user_id: int, bot_username: str = "@MyMyMyMyisnothingbhaibot"):
        """Get detailed expiry info for a user"""
        user = self.users.find_one({"user_id": user_id, "bot_username": bot_username})
        if not user or 'expiry_date' not in user: return None
        expiry = user['expiry_date']
        if isinstance(expiry, str):
            expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        return {"name": user.get('name'), "expiry_date": expiry.strftime("%d-%m-%Y"), "is_active": expiry > datetime.now()}

    def is_admin(self, user_id: int) -> bool:
        """Check if user is owner or admin"""
        return user_id == OWNER_ID or user_id in ADMINS

    def close(self):
        """Close connection"""
        if self.client:
            self.client.close()

# ☁ Final Initialization
try:
    db = Database()
except Exception as e:
    print(f"Fatal Error: {e}")
    raise
