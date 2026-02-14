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
# Channel Join Check
# ==============================
async def is_user_joined(bot, user_id: int):
    try:
        member = await bot.get_chat_member(MAIN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
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

    if update.callback_query:
        await update.callback_query.message.reply_text(
            "🎬 Welcome to Income Hub\n\nChoose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.message.reply_text(
            "🎬 Welcome to Income Hub\n\nChoose an option:",
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
            await query.message.delete()
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
# Main Runner (Render Safe)
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot Running Stable...")

    app.run_polling()


if __name__ == "__main__":
    main()
