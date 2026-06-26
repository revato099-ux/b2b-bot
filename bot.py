  async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buyurtmalar"""
    await update.message.reply_text(
        "📋 MENING BUYURTMALARIM\n\n"
        "🔄 Hozircha buyurtmalar mavjud emas.\n\n"
        "/catalog orqali yangi buyurtma berishingiz mumkin."
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    await update.message.reply_text(
        "🔧 ADMIN PANEL\n\n"
        "Google Sheets'ni oching:\n"
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit\n\n"
        "📊 Tablar:\n"
        "• MAHSULOTLAR - Mahsulotlarni boshqarish\n"
        "• OMBORLAR - Omborlar\n"
        "• DO'KONLAR - Roʻyxatga oʻtgan doʻkonlar\n"
        "• BUYURTMALAR - Barcha buyurtmalar"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam"""
    await update.message.reply_text(
        "❓ YORDAM\n\n"
        "/start - Botni boshlanishi\n"
        "/register - Doʻkon roʻyxatidan oʻtish\n"
        "/catalog - Mahsulotlar katalogi\n"
        "/orders - Mening buyurtmalarim\n"
        "/admin - Admin panel (admin uchun)\n"
        "/help - Bu xabar\n\n"
        "❓ Savollaringiz boʻlsa: @supportbot"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Standart xabar"""
    await update.message.reply_text(
        "Iltimos, buyruqlardan birini tanlang:\n"
        "/catalog - Mahsulotlar\n"
        "/orders - Buyurtmalar\n"
        "/help - Yordam"
    )

# ============= MAIN =============
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Register conversation
    register_conv = ConversationHandler(
        entry_points=[CommandHandler("register", register_start)],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            REG_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_address)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_phone)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    
    # Catalog conversation
    catalog_conv = ConversationHandler(
        entry_points=[CommandHandler("catalog", catalog)],
        states={
            PRODUCT_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_quantity)],
            ORDER_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_quantity)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(register_conv)
    app.add_handler(catalog_conv)
    app.add_handler(CommandHandler("orders", orders))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(product_selected, pattern=r"^product_"))
    app.add_handler(CallbackQueryHandler(order_confirm, pattern=r"^(confirm|cancel)_order$"))
    
    # Default handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Bot ishga tushdi...")
    app.run_polling()

if name == "main":
    main()