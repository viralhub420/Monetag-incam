import threading  # নতুন যোগ করা হয়েছে
from flask import Flask # নতুন যোগ করা হয়েছে
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import BOT_TOKEN, MAIN_CHANNEL
from user_manager import (
    create_user,
    update_last_active,
    set_join_status,
    get_user_data,
)

# ==============================
# ১. রেন্ডারের জন্য ফ্লাস্ক সার্ভার (জরুরি)
# ==============================
webapp = Flask(__name__)

@webapp.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # রেন্ডার এই ১০০০০ পোর্টটিই খোঁজে
    webapp.run(host='0.0.0.0', port=10000)

# ==============================
# আপনার আগের সব ফাংশন (start, is_user_joined, ইত্যাদি) ঠিক থাকবে
# ==============================
async def is_user_joined(bot, user_id: int):
    try:
        member = await bot.get_chat_member(MAIN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    create_user(user_id)
    update_last_active(user_id)
    joined = await is_user_joined(context.bot, int(user_id))
    if not joined:
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{MAIN_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ Joined", callback_data="check_join")]
        ]
        await update.message.reply_text("❌ আগে আমাদের চ্যানেলে যোগ দিন।", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    set_join_status(user_id, True)
    await show_main_menu(update)

async def show_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("👤 My Profile", callback_data="profile")],
        [InlineKeyboardButton("💰 Withdraw", callback_data="withdraw")]
    ]
    msg = "🎬 Welcome to Income Hub\n\nChoose an option:"
    if update.callback_query:
        await update.callback_query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    update_last_active(user_id)
    if query.data == "check_join":
        joined = await is_user_joined(context.bot, int(user_id))
        if joined:
            set_join_status(user_id, True)
            await query.message.delete()
            await show_main_menu(update)
        else:
            await query.answer("❌ এখনো চ্যানেলে যোগ দেননি!", show_alert=True)
    elif query.data == "profile":
        user_data = get_user_data(user_id)
        msg = f"👤 User ID: {user_id}\n⭐ Points: {user_data.get('points', 0)}\n📅 Created: {user_data.get('created_at')}"
        await query.message.reply_text(msg)
    elif query.data == "withdraw":
        user_data = get_user_data(user_id)
        points = user_data.get("points", 0)
        if points < 2000:
            await query.message.reply_text(f"❌ Minimum withdraw is 2000 points.\nYour current points: {points}")
        else:
            await query.message.reply_text("✅ Withdraw request received.\nAdmin will review manually.")

# ==============================
# ২. মেইন রানার (রেন্ডার ফ্রেন্ডলি)
# ==============================
def main():
    # ফ্ল্যাস্ক সার্ভার আলাদা থ্রেডে চালু হবে
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Running Stable...")
    
    # drop_pending_updates=True দিলে Conflict এরর হবে না
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
            
