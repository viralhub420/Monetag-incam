import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
MAIN_CHANNEL = os.getenv("MAIN_CHANNEL")

DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing in environment variables")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in environment variables")
