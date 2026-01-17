from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler
from datetime import datetime
import asyncio
import os

from db import db
from vars import *

async def handle_subscription_end(client: Client, user_id: int):
    try:
        # এখানে আপনার নিজস্ব বটের ইউজারনেম ব্যবহার করা হয়েছে
        await client.send_message(
            user_id,
            f"**⚠️ মেম্বারশিপ শেষ হয়েছে**\n\n"
            f"আপনার সাবস্ক্রিপশন শেষ। পুনরায় সচল করতে {BOT_USERNAME} এর অ্যাডমিনের সাথে যোগাযোগ করুন।"
        )
    except Exception:
        pass

# Command to add a new user
async def add_user_cmd(client: Client, message: Message):
    """বটে নতুন ইউজার যোগ করার কমান্ড"""
    try:
        # মালিকানা এবং অ্যাডমিন চেক
        if not db.is_admin(message.from_user.id):
            await message.reply_text("<b>❌ দুঃখিত, আপনি অ্যাডমিন নন!</b>")
            return

        args = message.text.split()[1:]
        if len(args) != 2:
            await message.reply_text(
                "<b>❌ সঠিক ফরম্যাট ব্যবহার করুন:</b>\n"
                "<code>/add user_id days</code>\n\n"
                "<b>উদাহরণ:</b>\n"
                "<code>/add 123456789 30</code>"
            )
            return

        user_id = int(args[0])
        days = int(args[1])
        bot_username = client.me.username

        try:
            user = await client.get_users(user_id)
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
        except:
            name = f"User {user_id}"

        # ডাটাবেসে ইউজার যোগ করা
        success, expiry_date = db.add_user(user_id, name, days, bot_username)
        
        if success:
            expiry_str = expiry_date.strftime("%d-%m-%Y %H:%M:%S")
            await message.reply_text(
                f"<b>✅ ইউজার সফলভাবে যুক্ত হয়েছে!</b>\n\n"
                f"👤 নাম: {name}\n"
                f"🆔 আইডি: <code>{user_id}</code>\n"
                f"📅 মেয়াদ: {expiry_str}"
            )

            try:
                await client.send_message(
                    user_id,
                    f"<b>🎉 অভিনন্দন! আপনার সাবস্ক্রিপশন সচল হয়েছে।</b>\n\n"
                    f"📅 মেয়াদ শেষ হবে: {expiry_str}\n"
                    f"🤖 বট: {BOT_USERNAME}"
                )
            except Exception as e:
                print(f"Failed to notify user {user_id}: {str(e)}")
        else:
            await message.reply_text("❌ ডাটাবেসে ইউজার যোগ করা সম্ভব হয়নি।")

    except ValueError:
        await message.reply_text("❌ আইডি এবং দিন সংখ্যা হিসেবে লিখুন।")
    except Exception as e:
        await message.reply_text(f"❌ এরর: {str(e)}")

# Command to remove a user
async def remove_user_cmd(client: Client, message: Message):
    """ইউজার রিমুভ করার কমান্ড"""
    try:
        if not db.is_admin(message.from_user.id):
            await message.reply_text("❌ আপনার এই কমান্ড ব্যবহারের ক্ষমতা নেই।")
            return

        args = message.text.split()[1:]
        if len(args) != 1:
            await message.reply_text("<b>ব্যবহার:</b> <code>/remove user_id</code>")
            return

        user_id = int(args[0])
        if db.remove_user(user_id, client.me.username):
            await message.reply_text(f"✅ ইউজার {user_id} কে রিমুভ করা হয়েছে।")
        else:
            await message.reply_text(f"❌ এই আইডির কোনো ইউজার পাওয়া যায়নি।")

    except Exception as e:
        await message.reply_text(f"❌ এরর: {str(e)}")

# Command to list all users
async def list_users_cmd(client: Client, message: Message):
    """সব ইউজারের লিস্ট দেখা"""
    try:
        if not db.is_admin(message.from_user.id):
            return

        users = db.list_users(client.me.username)
        if not users:
            await message.reply_text("📝 কোনো ইউজার পাওয়া যায়নি।")
            return

        user_list = f"<b>📝 {BOT_USERNAME} ইউজার লিস্ট</b>\n\n"
        for user in users:
            expiry = user['expiry_date']
            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
            
            remaining = expiry - datetime.now()
            days_left = remaining.days
            
            user_list += (
                f"👤 {user['name']}\n"
                f"🆔 <code>{user['user_id']}</code>\n"
                f"⏳ বাকি: {days_left} দিন\n"
                f"───────────────\n"
            )

        await message.reply_text(user_list)
    except Exception as e:
        await message.reply_text(f"❌ এরর: {str(e)}")

# Command to check user's plan
async def my_plan_cmd(client: Client, message: Message):
    """নিজের মেম্বারশিপ স্ট্যাটাস দেখা"""
    try:
        user = db.get_user(message.from_user.id, client.me.username)
        if not user:
            await message.reply_text(f"❌ আপনার কোনো একটিভ প্ল্যান নেই। যোগাযোগ: {BOT_USERNAME}")
            return

        expiry = user['expiry_date']
        if isinstance(expiry, str):
            expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        days_left = (expiry - datetime.now()).days

        await message.reply_text(
            f"<b>📱 আপনার মেম্বারশিপ ডিটেইলস</b>\n\n"
            f"👤 নাম: {user['name']}\n"
            f"⏳ বাকি আছে: {max(0, days_left)} দিন\n"
            f"📅 মেয়াদ শেষ: {expiry.strftime('%d-%m-%Y')}"
        )
    except Exception as e:
        await message.reply_text(f"❌ এরর: {str(e)}")

# Decorator for checking user authorization
def check_auth():
    def decorator(func):
        async def wrapper(client, message, *args, **kwargs):
            bot_info
