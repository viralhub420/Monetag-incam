import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# আপনার নিজের ফাইলগুলো থেকে ইমপোর্ট
from config import BOT_TOKEN, MAIN_CHANNEL
from user_manager import (
    create_user,
    update_last_active,
    set_join_status,
    get_user_data,
)
from keep_alive import keep_alive  # আপনার keep_alive.py ফাইল থেকে ইমপোর্ট

# লগিং সেটআপ (যাতে এরর হলে লগে দেখা যায়)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==============================
# Channel Join Check
# ==============================
async def is_user_joined(bot, user_id: int):
    try:
        member = await bot.get_chat_member(MAIN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Join check error: {e}")
        return False

# ==============================
# Start Command
# ==============================
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

        await update.message.reply_text(
            "❌ আগে আমাদের চ্যানেলে যোগ দিন।",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    set_join_status(user_id, True)
    await show_main_menu(update)

# ==============================
# Main Menu
# ==============================
async def show_main_menu(update: Update):
    keyboard = [
        [InlineKeyboardButton("👤 My Profile", callback_data="profile")],
        [InlineKeyboardButton("💰 Withdraw", callback_data="withdraw")]
    ]
    
    text = "🎬 Welcome to Income Hub\n\nChoose an option:"

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

# ==============================
# Button Handler
# ==============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    update_last_active(user_id)

    if query.data == "check_join":
        joined = await is_user_joined(context.bot, int(user_id))

        if joined:
            set_join_status(user_id, True)
            try:
                await query.message.delete()
            except:
                pass
            await show_main_menu(update)
        else:
            await query.answer("❌ এখনো চ্যানেলে যোগ দেননি!", show_alert=True)

    elif query.data == "profile":
        user_data = get_user_data(user_id)
        msg = (
            f"👤 User ID: {user_id}\n"
            f"⭐ Points: {user_data.get('points', 0)}\n"
            f"📅 Created: {user_data.get('created_at')}"
        )
        await query.message.reply_text(msg)

    elif query.data == "withdraw":
        user_data = get_user_data(user_id)
        points = user_data.get("points", 0)
        MIN_WITHDRAW = 2000

        if points < MIN_WITHDRAW:
            await query.message.reply_text(
                f"❌ Minimum withdraw is {MIN_WITHDRAW} points.\n"
                f"Your current points: {points}"
            )
        else:
            await query.message.reply_text(
                "✅ Withdraw request received.\nAdmin will review manually."
            )

# ==============================
# Main Runner
# ==============================
def main():
    # ১. ফ্লাস্ক সার্ভার চালু করা (রেন্ডারের জন্য জরুরি)
    keep_alive()
    print("Keep Alive Server Started...")

    # ২. বট অ্যাপ্লিকেশন তৈরি
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ৩. হ্যান্ডলার যোগ করা
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Running Stable...")

    # ৪. পোলিং শুরু করা (drop_pending_updates=True কনফ্লিক্ট মেটায়)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
