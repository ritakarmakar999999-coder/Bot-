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

class Database:
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.client: Optional[MongoClient] = None
        self.db: Optional[MongoDatabase] = None
        self.users: Optional[Collection] = None
        self.settings: Optional[Collection] = None
        self._connect_with_retry(max_retries, retry_delay)
        
    def _connect_with_retry(self, max_retries: int, retry_delay: float):
        for attempt in range(1, max_retries + 1):
            try:
                print(f"{Fore.YELLOW}⌛ Attempt {attempt}/{max_retries}: Connecting to MongoDB...{Style.RESET_ALL}")
                
                # 🛠️ SSL এরর ফিক্স করার জন্য প্যারামিটার যোগ করা হয়েছে
                self.client = MongoClient(
                    MONGO_URL,
                    serverSelectionTimeoutMS=20000,
                    tls=True,
                    tlsAllowInvalidCertificates=True, # এটি SSL এরর সমাধান করবে
                    tlsCAFile=certifi.where(),
                    retryWrites=True
                )
                
                self.client.server_info()
                self.db = self.client.get_database('My_Private_Bot_DB')
                self.users = self.db['users']
                self.settings = self.db['user_settings']
                
                print(f"{Fore.GREEN}✓ MongoDB Connected Successfully!{Style.RESET_ALL}")
                return
                
            except Exception as e:
                print(f"{Fore.RED}✕ Connection failed: {str(e)}{Style.RESET_ALL}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError("Could not connect to MongoDB.")

    def is_user_authorized(self, user_id: int, bot_username: str = "@MyMyMyMyisnothingbhaibot") -> bool:
        if user_id == OWNER_ID or user_id in ADMINS: return True
        user = self.users.find_one({"user_id": user_id})
        if not user or 'expiry_date' not in user: return False
        expiry = user['expiry_date']
        return expiry > datetime.now()

    def add_user(self, user_id: int, name: str, days: int):
        expiry_date = datetime.now() + timedelta(days=days)
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "expiry_date": expiry_date}},
            upsert=True
        )
        return True, expiry_date

    def is_admin(self, user_id: int) -> bool:
        return user_id == OWNER_ID or user_id in ADMINS

# DB Instance
db = Database()
