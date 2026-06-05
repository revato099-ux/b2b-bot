import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8986020797:AAHXwQy7s4vX4fs1uG_25ZS1pwEtjECiV4A"
ADMIN_ID = 8327031433

logging.basicConfig(format="%(asctime)s — %(levelname)s — %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

PRODUCTS = {
    "Yegulik": {
        "🧀 Pishiq (Solid)": 45000,
        "🥐 Non (Somsa)": 8000,
        "🥚 Tuxum (10 dona)": 28000,
        "🍯 Asal (1 kg)": 55000,
        "🥛 Yogʻurt": 15000,
    },
    "Sabzavotlar": {
        "🍅 Pomidor (1 kg)": 18000,
        "🥕 Sabzi (1 kg)": 12000,
        "🥦 Brokkoli": 22000,
    },
    "Mevalar": {
        "🍎 Alma (1 kg)": 22000,
        "🍊 Apelsin (1 kg)": 28000,
        "🍇 Uzum (1 kg)": 35000,
    },
    "Gadgetlar": {
        "📱 Samsung Galaxy": 4200000,
        "🎧 Quloqchin Pro": 350000,
    },
}

STORES = [
    {"id": 1, "name": "🏪 Oʻzbek Bozori", "city": "Toshkent"},
    {"id": 2, "name": "🏬 Samarqand Doʻkoni", "city": "Samarqand"},
    {"id": 3, "name": "🛒 Andijon Savdo", "city": "Andijon"},
]

users_db = {}
orders_db = []
carts = {}

def is_registered(user_id):
    return user_id in users_db and users_db[user_id].get("registered", False)

def get_main_keyboard():
    keyboard = [
        ["🛍 Katalog", "🛒 Buyurtmalarim"],
        ["🚚 Yetkazish", "💬 Yordam"],
        ["📱 Ilovani Ochish", "📞 Aloqa"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def new_order_id():
    return f"B2B-{len(orders_db)+1001}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_registered(user_id):
        name = users_db[user_id]["name"]
        await update.message.reply_text(
            f"👋 Xush kelibsiz, *{name}*!\n\nQuyidagi tugmalardan birini tanlang 👇",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "🎉 *B2B MARKET botiga xush kelibsiz!*\n\nRo'yxatdan o'tish uchun *ismingizni* yuboring:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["reg_step"] = "name"

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["reg_name"] = text
    context.user_data["reg_step"] = "phone"
    phone_kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        f"✅ Ism: *{text}*\n\n📞 Telefon raqamingizni yuboring:",
        parse_mode="Markdown",
        reply_markup=phone_kb
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    name = context.user_data.get("reg_name", user.first_name)
    users_db[user.id] = {
        "name": name,
        "phone": contact.phone_number,
        "registered": True,
        "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    await update.message.reply_text(
        f"🎊 *Roʻyxatdan oʻtdingiz!*\n\n👤 {name}\n📞 {contact.phone_number}",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 *Yangi foydalanuvchi!*\n👤 {name}\n📞 {contact.phone_number}\n🆔 {user.id}",
        parse_mode="Markdown"
    )
    context.user_data.pop("reg_step", None)

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"📂 {cat}", callback_data=f"cat_{cat}")] for cat in PRODUCTS]
    keyboard.append([InlineKeyboardButton("🛒 Savatcham", callback_data="view_cart")])
    
    if update.message:
        await update.message.reply_text(
            "🗂 *Mahsulot Katalogi*\n\nKategoriyani tanlang 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.callback_query.message.edit_text(
            "🗂 *Mahsulot Katalogi*\n\nKategoriyani tanlang 👇",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_name = query.data.replace("cat_", "")
    keyboard = []
    for prod, price in PRODUCTS[cat_name].items():
        keyboard.append([
            InlineKeyboardButton(prod, callback_data=f"prod_{cat_name}_{prod}"),
            InlineKeyboardButton(f"{price:,} soʻm", callback_data="info"),
        ])
    keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back_catalog")])
    
    await query.message.edit_text(
        f"📂 *{cat_name}*\n\nMahsulotni tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Savatchaga qoʻshildi!")
    user_id = query.from_user.id
    _, cat_name, prod_name = query.data.split("_", 2)
    price = PRODUCTS[cat_name][prod_name]
    
    if user_id not in carts:
        carts[user_id] = {}
    carts[user_id][prod_name] = carts[user_id].get(prod_name, 0) + 1
    cart_count = sum(carts[user_id].values())
    
    await query.message.edit_text(
        f"✅ *{prod_name}* qoʻshildi!\n💰 {price:,} soʻm\n🛒 Savat: {cart_count} ta",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 Savatchani koʻrish", callback_data="view_cart")],
            [InlineKeyboardButton("⬅️ Katalog", callback_data="back_catalog")],
        ])
    )

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = carts.get(user_id, {})
    
    if not cart:
        await query.message.edit_text(
            "🛒 *Savatcha boʻsh!*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛍 Katalog", callback_data="back_catalog")]])
        )
        return
    
    total = 0
    text = "🛒 *Savatcham:*\n\n"
    for prod, qty in cart.items():
        price = next((p for cat in PRODUCTS.values() for n, p in cat.items() if n == prod), 0)
        sub = price * qty
        total += sub
        text += f"• {prod} × {qty} = {sub:,} soʻm\n"
    
    text += f"\n💰 *Jami: {total:,} soʻm*"
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Buyurtma Berish", callback_data="checkout")],
            [InlineKeyboardButton("🗑 Tozalash", callback_data="clear_cart")],
            [InlineKeyboardButton("⬅️ Katalog", callback_data="back_catalog")],
        ])
    )

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑 Savatcha tozalandi!")
    carts.pop(query.from_user.id, None)
    await catalog(update, context)

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton(s["name"], callback_data=f"store_{s['id']}")] for s in STORES]
    keyboard.append([InlineKeyboardButton("❌ Bekor", callback_data="back_catalog")])
    
    await query.message.edit_text(
        "🏪 *Qaysi doʻkondan buyurtma berasiz?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    store_id = int(query.data.replace("store_", ""))
    store = next(s for s in STORES if s["id"] == store_id)
    cart = carts.get(user_id, {})
    
    total = sum(
        next((p for cat in PRODUCTS.values() for n, p in cat.items() if n == prod), 0) * qty
        for prod, qty in cart.items()
    )
    
    order_id = new_order_id()
    order = {
        "id": order_id,
        "user_id": user_id,
        "store": store["name"],
        "products": dict(cart),
        "total": total,
        "status": "Qabul Qilindi",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    orders_db.append(order)
    carts.pop(user_id, None)
    user_info = users_db.get(user_id, {})
    
    await query.message.edit_text(
        f"🎉 *Buyurtma berildi!*\n\n📋 Raqam: `{order_id}`\n🏪 {store['name']}\n💰 {total:,} soʻm\n🚦 Qabul Qilindi\n\n📦 Yetkazib berish: 2-24 soat ✅",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 Buyurtmalarim", callback_data="my_orders")],
            [InlineKeyboardButton("🛍 Yana xarid", callback_data="back_catalog")],
        ])
    )
    
    items_text = "\n".join(f"  • {p} × {q}" for p, q in order["products"].items())
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🛎 *YANGI BUYURTMA!*\n\n📋 {order_id}\n👤 {user_info.get('name', '?')}\n📞 {user_info.get('phone', '?')}\n🏪 {store['name']}\n📦\n{items_text}\n💰 {total:,} soʻm\n📅 {order['date']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_confirm_{order_id}")],
            [InlineKeyboardButton("❌ Rad etish", callback_data=f"admin_reject_{order_id}")],
        ])
    )

async def admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Ruxsat yoʻq!", show_alert=True)
        return
    
    parts = query.data.split("_", 2)
    action = parts[1]
    order_id = parts[2]
    order = next((o for o in orders_db if o["id"] == order_id), None)
    
    if not order:
        return
    
    if action == "confirm":
        order["status"] = "Tayyorlanmoqda"
        user_msg = f"✅ *Buyurtmangiz tasdiqlandi!*\n📋 {order_id}\n🚦 Tayyorlanmoqda"
    else:
        order["status"] = "Bekor Qilindi"
        user_msg = f"❌ *Buyurtmangiz rad etildi.*\n📋 {order_id}"
    
    await context.bot.send_message(chat_id=order["user_id"], text=user_msg, parse_mode="Markdown")
    await query.message.edit_reply_markup(reply_markup=None)

async def my_orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    u_orders = [o for o in orders_db if o["user_id"] == user_id]
    
    if not u_orders:
        text = "📦 *Buyurtmalar yoʻq.*\n\n/catalog orqali xarid qiling!"
    else:
        emoji = {"Qabul Qilindi": "🟡", "Tayyorlanmoqda": "🔵", "Yoʻlda": "🚚", "Yetkazildi": "✅", "Bekor Qilindi": "❌"}
        text = "📦 *Buyurtmalarim:*\n\n"
        for o in reversed(u_orders[-5:]):
            text += f"{emoji.get(o['status'], '📋')} *{o['id']}* — {o['status']}\n   💰 {o['total']:,} soʻm | {o['date']}\n\n"
    
    msg = update.message or update.callback_query.message
    await msg.reply_text(text, parse_mode="Markdown")

async def delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active = [o for o in orders_db if o["user_id"] == user_id and o["status"] not in ["Yetkazildi", "Bekor Qilindi"]]
    
    if not active:
        await update.message.reply_text(
            "🚚 *Faol buyurtma yoʻq.*\n\n/orders — barcha buyurtmalar",
            parse_mode="Markdown"
        )
        return
    
    steps = ["Qabul Qilindi", "Tayyorlanmoqda", "Yoʻlda", "Yetkazildi"]
    text = "🚚 *Faol Buyurtmalar:*\n\n"
    for o in active:
        idx = steps.index(o["status"]) if o["status"] in steps else 0
        prog = "".join("🟢" if i <= idx else "⚪" for i in range(4))
        text += f"📋 *{o['id']}*\n{prog}\n*{o['status']}* | {o['total']:,} soʻm\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 *Yordam Markazi*\n\nQanday yordam kerak?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Operator bilan suhbat", callback_data="support_chat")],
            [InlineKeyboardButton("❓ Tez-tez soʻraladigan", callback_data="support_faq")],
            [InlineKeyboardButton("📞 Telefon raqam", callback_data="support_phone")],
            [InlineKeyboardButton("🐛 Muammo bildirish", callback_data="support_bug")],
        ])
    )

async def support_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    back = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data="back_support")]])
    
    if action == "support_faq":
        await query.message.edit_text(
            "❓ *Tez-tez soʻraladigan savollar:*\n\n"
            "1️⃣ *Yetkazish vaqti?* → Tezkor 2-4 soat | Standart 24 soat\n\n"
            "2️⃣ *Bekor qilish?* → Tayyorlanmoqda bosqichigacha\n\n"
            "3️⃣ *Toʻlov usullari?* → Karta, Naqd, Hisobdan\n\n"
            "4️⃣ *Qaytarish?* → 24 soat ichida",
            parse_mode="Markdown",
            reply_markup=back
        )
    elif action == "support_phone":
        await query.message.edit_text(
            "📞 *Aloqa:*\n\n☎️ +998 71 123-45-67\n📱 +998 90 123-45-67\n⏰ 09:00—21:00",
            parse_mode="Markdown",
            reply_markup=back
        )

async def open_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 *B2B Market Ilovasi*\n\nTo'liq imkoniyatlar uchun ilovani oching!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📱 Ilovani Ochish", web_app=WebAppInfo(url="https://sizning-ilovangiz.up.railway.app"))
        ]])
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *Aloqa:*\n\n☎️ +998 71 123-45-67\n📱 +998 90 123-45-67\n📧 info@b2bmarket.uz\n🌐 www.b2bmarket.uz",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📍 Xaritada", url="https://maps.google.com")],
            [InlineKeyboardButton("📢 Kanalimiz", url="https://t.me/b2bmarket_uz")],
        ])
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    rev = sum(o["total"] for o in orders_db if o["status"] == "Yetkazildi")
    await update.message.reply_text(
        f"📊 *ADMIN STATISTIKA*\n\n👥 Foydalanuvchilar: {len(users_db)}\n📦 Jami buyurtmalar: {len(orders_db)}\n✅ Yetkazilgan: {sum(1 for o in orders_db if o['status']=='Yetkazildi')}\n💰 Daromad: {rev:,} soʻm",
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if context.user_data.get("reg_step") == "name":
        await handle_registration(update, context)
        return
    
    if not is_registered(user_id):
        await start(update, context)
        return
    
    routes = {
        "🛍 Katalog": catalog,
        "🛒 Buyurtmalarim": my_orders_cmd,
        "🚚 Yetkazish": delivery,
        "💬 Yordam": support,
        "📱 Ilovani Ochish": open_app,
        "📞 Aloqa": contact,
    }
    
    if text in routes:
        await routes[text](update, context)

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    
    if data == "back_catalog":
        await catalog(update, context)
    elif data == "view_cart":
        await view_cart(update, context)
    elif data == "clear_cart":
        carts.pop(update.callback_query.from_user.id, None)
        await catalog(update, context)
    elif data == "checkout":
        await checkout(update, context)
    elif data == "my_orders":
        await my_orders_cmd(update, context)
    elif data.startswith("cat_"):
        await show_category(update, context)
    elif data.startswith("prod_"):
        await add_to_cart(update, context)
    elif data.startswith("store_"):
        await confirm_order(update, context)
    elif data.startswith("support_") or data == "back_support":
        await support_action(update, context)
    elif data.startswith("admin_"):
        await admin_action(update, context)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", catalog))
    app.add_handler(CommandHandler("orders", my_orders_cmd))
    app.add_handler(CommandHandler("delivery", delivery))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("app", open_app))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("stats", admin_stats))
    
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("🤖 B2B Market Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
  
