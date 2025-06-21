from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import os

# متغيرات البيئة
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# بيانات المواد لكل فصل
semester_data = {
    "السابع": [
        "اقتصاد هندسي", "تصميم خرسانة 2", "تصميم فولاذ 1", "حساب كميات", "فكر إسلامي",
        "ميكانيكا تربة 2", "هندسة طرق 1", "هيدروليكا 1", "واقع إسلامي"
    ],
    "الثامن": [
        "إدارة تشييد", "تصميم خرسانة 3", "تصميم فولاذ 2", "دراسات قرآنية",
        "هندسة بيئية", "هندسة طرق 2", "هيدروليكا 2"
    ]
}

# بدء البوت - الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 الفصل السابع", callback_data='السابع')],
        [InlineKeyboardButton("📘 الفصل الثامن", callback_data='الثامن')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📖 اختر الفصل الدراسي:", reply_markup=reply_markup)

# عند الضغط على الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in semester_data:
        buttons = [[InlineKeyboardButton(subject, callback_data="none")] for subject in semester_data[data]]
        markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(f"📘 مواد الفصل {data}:", reply_markup=markup)
    else:
        await query.edit_message_text("📌 سيتم إضافة المحتوى لاحقًا.")

# إعداد التطبيق باستخدام Flask
app = Flask(__name__)
from telegram.ext import Application
telegram_app = ApplicationBuilder().token(TOKEN).build()

# إضافة الأوامر
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# مسار Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"

# الصفحة الرئيسية
@app.route("/")
def home():
    return "✅ البوت يعمل الآن باستخدام Webhook!"

# تعيين Webhook عند أول تشغيل
@app.before_first_request
def set_webhook():
    telegram_app.bot.set_webhook(url=WEBHOOK_URL)

# تشغيل التطبيق
if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
