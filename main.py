import os
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from telegram.ext import Defaults
import asyncio

# إعداد التوكن وتهيئة التطبيق
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # مثال: https://yourapp.up.railway.app

# مجلدات الفصول الدراسية
semesters_paths = {
    "السابع": "semester7",
    "الثامن": "semester8"
}

# إعداد FastAPI
app = FastAPI()

# إعداد البوت
tg_app = Application.builder().token(TOKEN).defaults(Defaults(parse_mode="HTML")).build()

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 الفصل السابع", callback_data="السابع")],
        [InlineKeyboardButton("📘 الفصل الثامن", callback_data="الثامن")]
    ]
    await update.message.reply_text("📖 اختر الفصل الدراسي:", reply_markup=InlineKeyboardMarkup(keyboard))

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in semesters_paths:
        folder_path = semesters_paths[data]
        if os.path.exists(folder_path):
            subjects = os.listdir(folder_path)
            buttons = [[InlineKeyboardButton(sub, callback_data=f"{data}|{sub}")] for sub in subjects]
            await query.edit_message_text(f"📘 مواد الفصل {data}:", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await query.edit_message_text("❌ لم يتم العثور على مجلد الفصل الدراسي.")

    elif "|" in data:
        semester, subject = data.split("|")
        folder_path = os.path.join(semesters_paths[semester], subject)

        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            if not files:
                await query.edit_message_text(f"📂 لا توجد ملفات للمادة {subject}.")
                return

            await query.edit_message_text(f"📤 يتم إرسال ملفات مادة {subject} الآن...")

            for filename in files:
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, "rb") as file:
                        await context.bot.send_document(chat_id=query.message.chat_id, document=InputFile(file), caption=filename)
                except Exception as e:
                    print(f"❌ فشل إرسال {filename}: {e}")
                    await context.bot.send_message(chat_id=query.message.chat_id, text=f"⚠️ تعذر إرسال الملف: {filename}")
        else:
            await query.edit_message_text("❌ لم يتم العثور على مجلد المادة.")

# تسجيل المعالجات
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CallbackQueryHandler(button_handler))

# نقطة استقبال Webhook من Telegram
@app.post(f"/{TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.update_queue.put(update)
    return "OK"

# إعداد Webhook عند التشغيل
@app.on_event("startup")
async def on_startup():
    await tg_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    asyncio.create_task(tg_app.initialize())  # بدء البوت

