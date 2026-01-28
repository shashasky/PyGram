# config/bot.py
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_MODE = os.getenv("BOT_MODE", "polling")