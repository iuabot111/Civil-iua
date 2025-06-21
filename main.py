import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from fastapi import FastAPI, Request
import uvicorn

# إعداد التوكن من متغيرات البيئة
TOKEN = "7336468743:AAEscQiBQMaY9pvgKt9SVKP1B-EoDrfZD6k"
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://civil-iua-production.up.railway.app{WEBHOOK_PATH}"

# مواد مع وصف مختصر
subject_info = {
    "اقتصاد هندسي": "شرح اقتصاد هندسي 📘...",
    "تصميم خرسانة 2": "شرح تصميم خرسانة 2 🧱...",
    "تصميم فولاذ 1": "شرح تصميم فولاذ 1 🔩...",
    "حساب كميات": "شرح حساب كميات 📏...",
    "فكر إسلامي": "شرح فكر إسلامي 🕌...",
    "ميكانيكا تربة 2": "شرح ميكانيكا تربة 2 🧪...",
    "هندسة طرق 1": "شرح هندسة طرق 1 🛣️...",
    "هيدروليكا 1": "شرح هيدروليكا 1 💧...",
    "واقع إسلامي": "شرح واقع إسلامي 🌍...",
    "إدارة تشييد": "شرح إدارة تشييد 🏗️...",
    "تصميم خرسانة 3": "شرح تصميم خرسانة 3 🧱...",
    "تصميم فولاذ 2": "شرح تصميم فولاذ 2 🔧...",
    "دراسات قرآنية": "شرح دراسات قرآنية 📖...",
    "هندسة بيئية": "شرح هندسة بيئية 🌱...",
    "هندسة طرق 2": "شرح هندسة طرق 2 🛤️...",
    "هيدروليكا 2": "شرح هيدروليكا 2 🚰...",
}

semesters = {
    "السابع": [k for k in subject_info if k in [
        "اقتصاد هندسي", "تصميم خرسانة 2", "تصميم فولاذ 1", "حساب كميات",
        "فكر إسلامي", "ميكانيكا تربة 2", "هندسة طرق 1", "هيدروليكا 1", "واقع إسلامي"]],
    "الثامن": [k for k in subject_info if k in [
        "إدارة تشييد", "تصميم خرسانة 3", "تصميم فولاذ 2", "دراسات قرآنية",
        "هندسة بيئية", "هندسة طرق 2", "هيدروليكا 2"]],
}

# الوظائف الأساسية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 الفصل السابع", callback_data="السابع")],
        [InlineKeyboardButton("📘 الفصل الثامن", callback_data="الثامن")]
    ]
    await update.message.reply_text("📖 اختر الفصل الدراسي:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in semesters:
        buttons = [[InlineKeyboardButton(sub, callback_data=sub)] for sub in semesters[data]]
        await query.edit_message_text(f"📘 مواد الفصل {data}:", reply_markup=InlineKeyboardMarkup(buttons))
    elif data in subject_info:
        await query.edit_message_text(subject_info[data])
    else:
        await query.edit_message_text("❌ لا توجد بيانات متاحة.")

# إنشاء البوت وتطبيق FastAPI
app = FastAPI()
bot_app = ApplicationBuilder().token(TOKEN).build()

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(button_handler))

@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    await bot_app.update_queue.put(Update.de_json(data, bot_app.bot))
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook set!")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
