import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

# --- अपनी डिटेल्स यहाँ भरें ---
API_ID = 27808422       # अपनी असली API ID यहाँ डालें (बिना कॉमा के नंबर)
API_HASH = "9cdb40d1613b62e03debc04b8ae68538" # अपना असली API HASH यहाँ डालें
BOT_TOKEN = "8995363789:AAHh0SIH4umZlJtoQdbpK71Eb9U-uh1p-Ag"
ADMIN_ID = 8279891640  

# Pyrogram क्लाइंट सेटअप
app = Client("selling_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DB_PATH = os.path.join(os.getcwd(), "selling_bot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS plans 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, caption TEXT, 
                       channels_count TEXT, channel_link TEXT, validity TEXT,
                       v1 TEXT, v2 TEXT, v3 TEXT, v4 TEXT, v5 TEXT, status TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings 
                      (key TEXT PRIMARY KEY, value TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_id', 'not_set')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('upi_name', 'not_set')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('qr_file_id', 'not_set')")
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Database Error: {e}")

# एडमिन स्टेट ट्रैकर
admin_state = {}

def get_main_menu_markup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM plans WHERE status='active'")
    active_plans = cursor.fetchall()
    conn.close()
    
    keyboard = []
    for plan in active_plans:
        keyboard.append([InlineKeyboardButton(f"✨ {plan[1]} — ₹{plan[2]}", callback_data=f"viewplan_{plan[0]}")])
    
    keyboard.append([
        InlineKeyboardButton("📖 How to Use", callback_data="how_to"),
        InlineKeyboardButton("🚨 Report Issue", callback_data="report")
    ])
    return InlineKeyboardMarkup(keyboard)

# --- /start कमांड ---
@app.on_message(filters.command("start") & filters.private)
async def user_start(client: Client, message: Message):
    user_name = message.from_user.first_name
    welcome_text = f"👋 Hello, **{user_name} HERE !!**\n\nChoose a plan to get started 👇"
    await message.reply_text(welcome_text, reply_markup=get_main_menu_markup(), parse_mode=None)

# --- /admin कमांड ---
@app.on_message(filters.command("admin") & filters.user(ADMIN_ID) & filters.private)
async def admin_panel(client: Client, message: Message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key='upi_id'")
    upi = cursor.fetchone()[0]
    cursor.execute("SELECT value FROM settings WHERE key='upi_name'")
    name = cursor.fetchone()[0]
    cursor.execute("SELECT value FROM settings WHERE key='qr_file_id'")
    qr = cursor.fetchone()[0]
    conn.close()
    
    keyboard = [
        [InlineKeyboardButton("➕ नया प्लान जोड़ें", callback_data="admin_addplan")],
        [
            InlineKeyboardButton(f"💳 UPI ID ({'✅' if upi!='not_set' else '❌'})", callback_data="admin_setupi"),
            InlineKeyboardButton(f"👤 Name ({'✅' if name!='not_set' else '❌'})", callback_data="admin_setname")
        ],
        [InlineKeyboardButton(f"🖼 QR Code ({'✅' if qr!='not_set' else '❌'})", callback_data="admin_setqr")]
    ]
    await message.reply_text("🛠 **एडमिन कंट्रोल पैनल**", reply_markup=InlineKeyboardMarkup(keyboard))

# --- बटन क्लिक्स (Callbacks) ---
@app.on_callback_query()
async def handle_callbacks(client: Client, call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. प्लान देखना और 5 वीडियो भेजना
    if call.data.startswith('viewplan_'):
        plan_id = call.data.split('_')[1]
        cursor.execute("SELECT name, price, caption, validity, v1, v2, v3, v4, v5 FROM plans WHERE id=?", (plan_id,))
        plan = cursor.fetchone()
        
        if plan:
            name, price, caption, validity, *videos = plan
            await call.message.reply_text(f"⏳ **आपके लिए {name} की डेमो वीडियोज़ लोड की जा रही हैं...**")
            
            for video in videos:
                if video and video != "None":
                    try:
                        await client.send_video(chat_id, video)
                    except Exception:
                        pass
            
            keyboard = [
                [InlineKeyboardButton("💳 Buy Now", callback_data=f"buy_{plan_id}")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
            caption_text = caption if caption and caption != "None" else "No description available."
            info_msg = f"📦 **Plan:** {name}\n💰 **Price:** ₹{price}\n⏳ **Validity:** {validity}\n\n📝 **Details:**\n{caption_text}"
            await client.send_message(chat_id, info_msg, reply_markup=InlineKeyboardMarkup(keyboard))
            
    elif call.data == "back_to_menu":
        user_name = call.from_user.first_name
        welcome_text = f"👋 Hello, **{user_name} HERE !!**\n\nChoose a plan to get started 👇"
        await call.message.edit_text(welcome_text, reply_markup=get_main_menu_markup())

    # 2. Buy Now पर क्लिक
    elif call.data.startswith('buy_'):
        plan_id = call.data.split('_')[1]
        cursor.execute("SELECT name, price, validity FROM plans WHERE id=?", (plan_id,))
        plan = cursor.fetchone()
        
        cursor.execute("SELECT value FROM settings WHERE key='upi_id'")
        upi_id = cursor.fetchone()[0]
        cursor.execute("SELECT value FROM settings WHERE key='upi_name'")
        upi_name = cursor.fetchone()[0]
        cursor.execute("SELECT value FROM settings WHERE key='qr_file_id'")
        qr_file_id = cursor.fetchone()[0]
        
        if plan:
            name, price, validity = plan
            pay_msg = (
                f"💳 **Payment Details**\n\n"
                f"📦 **Plan:** {name}\n"
                f"💰 **Amount:** ₹{price}\n"
                f"⏳ **Validity:** {validity}\n\n"
                f"📲 **UPI ID:** `{upi_id}`\n"
                f"👤 **Name:** {upi_name}\n\n"
                f"1️⃣ Pay ₹{price} to the UPI ID above\n"
                f"2️⃣ After payment, click ✅ I Have Paid"
            )
            keyboard = [
                [InlineKeyboardButton("✅ I Have Paid", callback_data=f"paid_{plan_id}")],
                [InlineKeyboardButton("🔙 Cancel", callback_data="back_to_menu")]
            ]
            
            if qr_file_id != "not_set":
                try:
                    await client.send_photo(chat_id, qr_file_id, caption=pay_msg, reply_markup=InlineKeyboardMarkup
