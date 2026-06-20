import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# Bot token
BOT_TOKEN = "8986020797:AAHXwQy7s4vX4fs1uG_25ZS1pwEtjECiV4A"  # @BotFather'dan oling
ADMIN_ID = 8327031433  # @userinfobot'dan oling

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(name)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum! B2B Market botiga xush kelibsiz!\n\n"
        "Buyruqlar:\n"
        "/catalog - Mahsulotlar katalogi\n"
        "/orders - Buyurtmalarim\n"
        "/support - Qo'llab-quvvatlash"
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📦 Mahsulotlar katalogi")

async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Sizning buyurtmalaringiz")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 Qo'llab-quvvatlash bo'limi")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Boshlash\n"
        "/catalog - Katalog\n"
        "/orders - Buyurtmalar\n"
        "/support - Qo'llab-quvvatlash\n"
        "/help - Yordam"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Siz yozgan: {text}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", catalog))
    app.add_handler(CommandHandler("orders", orders))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if name == 'main':
    main()