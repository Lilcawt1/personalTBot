
import asyncio
import logging
import nest_asyncio
nest_asyncio.apply()
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatMemberStatus

TOKEN = "7952135976:AAEYUqPS0RMV7s8Vaht_o5ygcJ5sZQoBPpc"
ADMINS = [6813030531, 7744364187, 5874160209]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

HELP_TEXT = """
🚨 دستورات مدیریت گروه:

/kick یا سیک 👢
🔹 اخراج کاربر (با ریپلای یا منشن)

/ban یا خارکصه 🔨
🔹 بن کردن کاربر

/mute یا خفه 🔇
🔹 میوت کردن کاربر

/reload ♻️
🔹 ریستارت ربات

/help یا راهنما ❓
🔹 مشاهده راهنمای دستورات (فقط برای ادمین‌ها)
"""

def is_admin(user_id):
    return user_id in ADMINS

def get_protection_message(target_id):
    if target_id == 6813030531:
        return "☺️💖 من نمیتونم قلب خدارو اخراج کنم"
    elif target_id in ADMINS:
        return "⚠️من نمیتونم خدا رو اخراج کنم"
    return None

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        await update.message.delete()

async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("ریپلای کن به پیام کاربر!")
        return
    target = update.message.reply_to_message.from_user
    msg = get_protection_message(target.id)
    if msg:
        await update.message.reply_text(msg)
        return
    await context.bot.ban_chat_member(update.effective_chat.id, target.id)
    await context.bot.unban_chat_member(update.effective_chat.id, target.id)
    await update.message.reply_text(
        f"{target.full_name} با لگد از گروه پرتاب شد 👢")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("ریپلای کن به پیام طرف!")
        return
    target = update.message.reply_to_message.from_user
    msg = get_protection_message(target.id)
    if msg:
        await update.message.reply_text(msg)
        return
    await context.bot.ban_chat_member(update.effective_chat.id, target.id)
    await update.message.reply_text(f"{target.full_name} به جهنم بن شد 🔨")

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "ریپلای کن به پیام کسی که باید خفه شه 😶")
        return
    target = update.message.reply_to_message.from_user
    msg = get_protection_message(target.id)
    if msg:
        await update.message.reply_text(msg)
        return
    permissions = ChatPermissions(can_send_messages=False)
    await context.bot.restrict_chat_member(update.effective_chat.id,
                                           target.id,
                                           permissions=permissions)
    await update.message.reply_text(f"{target.full_name} خفه شد 😶")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        await update.message.reply_text(HELP_TEXT)

async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_admin(update.effective_user.id):
        await update.message.reply_text("✅ روبات با موفقیت ریلود شد")

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                if update.effective_user.id not in ADMINS:
                    await update.message.reply_text(
                        "فقط ادمین‌های اصلی می‌تونن ربات رو اضافه کنن!")
                    await context.bot.leave_chat(update.effective_chat.id)

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler(["kick"], kick_user))
    app.add_handler(CommandHandler(["ban"], ban_user))
    app.add_handler(CommandHandler(["mute"], mute_user))
    app.add_handler(CommandHandler(["help"], help_command))
    app.add_handler(CommandHandler(["reload"], reload_command))

    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^سیک$"), kick_user))
    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^خارکصه$"), ban_user))
    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^خفه$"), mute_user))
    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^راهنما$"),
                       help_command))

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_join))
    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex(r"^پاک کن$"), delete))

    print("🤖 ربات با موفقیت اجرا شد.")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except RuntimeError as e:
        if str(e).startswith("This event loop is already running"):
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.get_event_loop().run_until_complete(run_bot())
        else:
            raise
