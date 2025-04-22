import random
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberAdministrator, ChatPermissions
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          ContextTypes, filters, CallbackQueryHandler,
                          Application)

BOT_TOKEN = '8123532822:AAHxdTxh_lQWfhoFojfxJoP4IaRR8YS7aT8'
OWNER_ID = 6143388752
AUTO_SEND_ENABLED = True
REGISTERED_CHATS = {"@DefendYourFaith"}

with open("shubuhat_part_1.txt", "r", encoding="utf-8") as f:
    RESPONSES = [r.strip() for r in f.read().split("🟥") if r.strip()]

current_index = 0  # مؤشر لتتبع الشبهة الحالية


def fetch_religious_content():
    global current_index
    if current_index >= len(RESPONSES):
        return "🛑 انتهت جميع الشبهات المتوفرة حالياً."

    content = RESPONSES[current_index]
    current_index += 1
    return "🟥" + content


async def clear_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    chat = update.effective_chat
    async for msg in chat.get_history(limit=100):
        try:
            await context.bot.delete_message(chat_id=chat.id,
                                             message_id=msg.message_id)
        except:
            continue
    await update.message.reply_text("✅ تم حذف رسائل المجموعة")


async def kick_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("أرسل الأمر مع الـ @ أو ID")
        return
    try:
        user_id = int(
            context.args[0]) if context.args[0].isdigit() else context.args[0]
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("✅ تم الطرد.")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الطرد: {str(e)}")


async def promote_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("أرسل الأمر مع الـ @ أو ID")
        return
    try:
        user_id = int(
            context.args[0]) if context.args[0].isdigit() else context.args[0]
        await context.bot.promote_chat_member(chat_id=update.effective_chat.id,
                                              user_id=user_id,
                                              can_manage_chat=True,
                                              can_delete_messages=True,
                                              can_invite_users=True,
                                              can_manage_video_chats=True)
        await update.message.reply_text("✅ تم الترقية.")
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الترقية: {str(e)}")


async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_SEND_ENABLED
    if update.effective_user.id != OWNER_ID:
        return
    AUTO_SEND_ENABLED = True
    await update.message.reply_text("✅ تم تفعيل الإرسال التلقائي.")


async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_SEND_ENABLED
    if update.effective_user.id != OWNER_ID:
        return
    AUTO_SEND_ENABLED = False
    await update.message.reply_text("🛑 تم إيقاف الإرسال التلقائي.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global AUTO_SEND_ENABLED
    query = update.callback_query
    await query.answer()
    if query.data == "enable":
        AUTO_SEND_ENABLED = True
        await query.edit_message_text("✅ تم تفعيل الإرسال التلقائي.")
    elif query.data == "disable":
        AUTO_SEND_ENABLED = False
        await query.edit_message_text("🛑 تم إيقاف الإرسال التلقائي.")


async def send_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    content = fetch_religious_content()
    for chat_id in REGISTERED_CHATS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=content)
        except Exception as e:
            await update.message.reply_text(
                f"❌ فشل الإرسال إلى {chat_id}: {str(e)}")
    await update.message.reply_text("✅ تم إرسال الشبهة الآن.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("✅ تفعيل الإرسال", callback_data="enable"),
        InlineKeyboardButton("🛑 إيقاف الإرسال", callback_data="disable")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    help_text = ("🛠️ قائمة الأوامر:\n"
                 "/enable - تفعيل الإرسال التلقائي\n"
                 "/disable - إيقاف الإرسال التلقائي\n"
                 "/sendnow - إرسال الشبهة التالية الآن\n"
                 "/clear - حذف رسائل المجموعة\n"
                 "/kick [ID أو @] - طرد عضو\n"
                 "/promote [ID أو @] - ترقية عضو\n"
                 "/help - عرض هذه القائمة")

    await update.message.reply_text(help_text, reply_markup=reply_markup)


async def auto_send_content(context: ContextTypes.DEFAULT_TYPE):
    if not AUTO_SEND_ENABLED:
        return
    content = fetch_religious_content()
    for chat_id in REGISTERED_CHATS:
        try:
            await context.bot.send_message(chat_id=chat_id, text=content)
            await context.bot.send_message(chat_id=OWNER_ID,
                                           text=f"📢 تم الإرسال إلى: {chat_id}")
        except Exception as e:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"⚠️ فشل الإرسال إلى {chat_id}: {str(e)}")


async def register_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    REGISTERED_CHATS.add(chat_id)
    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=
            f"✅ تم إضافة البوت إلى: {update.effective_chat.title or chat_id}")
    except:
        pass


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # تعريف job_queue هنا
    job_queue = app.job_queue
    app.add_handler(CommandHandler("sendnow", send_now))
    app.add_handler(CommandHandler("clear", clear_group))
    app.add_handler(CommandHandler("kick", kick_member))
    app.add_handler(CommandHandler("promote", promote_member))
    app.add_handler(CommandHandler("enable", enable))
    app.add_handler(CommandHandler("disable", disable))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, register_chat))

    # الآن استخدمه بأمان
    if job_queue:
        job_queue.run_repeating(auto_send_content, interval=20, first=10)

    app.run_polling()




if __name__ == "__main__":
    
    main()  # يشغّل البوت
