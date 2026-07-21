import os
import sys
import logging
import time
import json
import threading
import sqlite3
import requests
from datetime import datetime, timedelta
from io import BytesIO
import telebot
from telebot import types
import qrcode
from flask import Flask, render_template_string

# ==================== CONFIG ====================
# 🔴 YAHAN APNA BOT TOKEN DAALO
BOT_TOKEN = "8912326354:AAGxNKNCUwLVDBR6qaJLEbRyatjP8Ij94Do"

# 🔴 YAHAN FAMPAY API KEY DAALO
FAMPAY_API_KEY = "YOUR_API_KEY_HERE"
FAMPAY_VERIFY_URL = "https://fampay.anujbots.xyz/verify.php"

if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ BOT_TOKEN set karo! Line ~12 mein apna token daalo.")
    sys.exit(1)

if FAMPAY_API_KEY == "YOUR_API_KEY_HERE":
    print("⚠️ FAMPAY_API_KEY set nahi hai! Autopay verification disable rahega.")

ADMIN_IDS = []
DATABASE_PATH = 'bot_database.db'
PORT = int(os.getenv('PORT', 8080))
SECRET_KEY = os.urandom(24)

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        if os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute("SELECT 1")
                conn.close()
            except:
                os.remove(self.db_path)
        self.init_tables()
    
    def get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_tables(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            subscription_plan_id INTEGER,
            subscription_expiry TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_admin INTEGER DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            validity_days INTEGER NOT NULL,
            channel_link TEXT,
            description TEXT,
            media_json TEXT DEFAULT '[]',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            screenshot_file_id TEXT,
            order_id TEXT,
            status TEXT DEFAULT 'pending',
            admin_comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT
        )''')
        defaults = [
            ('welcome_image', ''),
            ('welcome_text', 'Welcome to Premium Bot! 🎉\n\nGet exclusive access to premium content\nAffordable plans starting at just ₹0'),
            ('bot_name', 'PREMIUM BOT'),
            ('upi_id', ''),
            ('qr_code', ''),
            ('delivery_link', ''),
            ('welcome_video', '')
        ]
        for key, val in defaults:
            c.execute('INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES (?, ?)', (key, val))
        conn.commit()
        conn.close()
        logger.info("✅ Database ready")
    
    def add_user(self, user_id, username='', first_name='', last_name=''):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
                 (user_id, username, first_name, last_name))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            cols = [d[0] for d in c.description]
            return dict(zip(cols, row))
        return None
    
    def get_all_users(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        cols = [d[0] for d in c.description]
        return [dict(zip(cols, row)) for row in rows]
    
    def set_admin(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def remove_admin(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('UPDATE users SET is_admin = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def get_admins(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT user_id, first_name, username FROM users WHERE is_admin = 1 ORDER BY created_at ASC')
        rows = c.fetchall()
        conn.close()
        return rows
    
    def is_admin(self, user_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        return row and row[0] == 1
    
    def update_subscription(self, user_id, plan_id, days):
        conn = self.get_conn()
        c = conn.cursor()
        expiry = (datetime.now() + timedelta(days=days)).isoformat()
        c.execute('UPDATE users SET subscription_plan_id = ?, subscription_expiry = ? WHERE user_id = ?',
                 (plan_id, expiry, user_id))
        conn.commit()
        conn.close()
        return expiry
    
    def add_plan(self, name, price, days, channel_link, description=''):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('INSERT INTO plans (name, price, validity_days, channel_link, description) VALUES (?, ?, ?, ?, ?)',
                 (name, price, days, channel_link, description))
        plan_id = c.lastrowid
        conn.commit()
        conn.close()
        return plan_id
    
    def get_plan(self, plan_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT * FROM plans WHERE plan_id = ? AND is_active = 1', (plan_id,))
        row = c.fetchone()
        conn.close()
        if row:
            cols = [d[0] for d in c.description]
            return dict(zip(cols, row))
        return None
    
    def get_all_plans(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT * FROM plans WHERE is_active = 1 ORDER BY price ASC')
        rows = c.fetchall()
        conn.close()
        cols = [d[0] for d in c.description]
        return [dict(zip(cols, row)) for row in rows]
    
    def update_plan(self, plan_id, **kwargs):
        conn = self.get_conn()
        c = conn.cursor()
        allowed = ['name', 'price', 'validity_days', 'channel_link', 'description', 'media_json']
        updates = []
        vals = []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k} = ?")
                vals.append(v)
        if updates:
            vals.append(plan_id)
            c.execute(f"UPDATE plans SET {', '.join(updates)} WHERE plan_id = ?", vals)
            conn.commit()
        conn.close()
    
    def delete_plan(self, plan_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('UPDATE plans SET is_active = 0 WHERE plan_id = ?', (plan_id,))
        conn.commit()
        conn.close()
    
    def add_media(self, plan_id, media_type, file_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT media_json FROM plans WHERE plan_id = ?', (plan_id,))
        row = c.fetchone()
        if row:
            media_list = json.loads(row[0]) if row[0] else []
            media_list.append({'type': media_type, 'file_id': file_id, 'added_at': datetime.now().isoformat()})
            c.execute('UPDATE plans SET media_json = ? WHERE plan_id = ?', (json.dumps(media_list), plan_id))
            conn.commit()
        conn.close()
    
    def get_plan_media(self, plan_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT media_json FROM plans WHERE plan_id = ?', (plan_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row[0]) if row[0] else []
        return []
    
    def add_payment(self, user_id, plan_id, amount, file_id, order_id=''):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('INSERT INTO payments (user_id, plan_id, amount, screenshot_file_id, order_id, status) VALUES (?, ?, ?, ?, ?, "pending")',
                 (user_id, plan_id, amount, file_id, order_id))
        payment_id = c.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def get_payment(self, payment_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT * FROM payments WHERE payment_id = ?', (payment_id,))
        row = c.fetchone()
        conn.close()
        if row:
            cols = [d[0] for d in c.description]
            return dict(zip(cols, row))
        return None
    
    def get_pending_payments(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            SELECT p.*, u.username, u.first_name, u.last_name, pl.name as plan_name
            FROM payments p
            JOIN users u ON p.user_id = u.user_id
            JOIN plans pl ON p.plan_id = pl.plan_id
            WHERE p.status = 'pending'
            ORDER BY p.created_at ASC
        ''')
        rows = c.fetchall()
        conn.close()
        cols = [d[0] for d in c.description]
        return [dict(zip(cols, row)) for row in rows]
    
    def verify_payment_with_fampay(self, order_id):
        """Verify payment via FamPay API"""
        if not FAMPAY_API_KEY or FAMPAY_API_KEY == "YOUR_API_KEY_HERE":
            return None, "FamPay API key not configured"
        try:
            url = f"{FAMPAY_VERIFY_URL}?order_id={order_id}&api_key={FAMPAY_API_KEY}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get('status') == 'success':
                return True, data.get('message', 'Verified')
            else:
                return False, data.get('message', 'Verification failed')
        except Exception as e:
            return None, f"API error: {str(e)}"
    
    def approve_payment(self, payment_id, skip_verify=False):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute('SELECT status, order_id FROM payments WHERE payment_id = ?', (payment_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                return False, "Payment not found"
            if row[0] != 'pending':
                conn.close()
                return False, f"Payment already {row[0]}"
            
            # FamPay verification (unless skipped)
            if not skip_verify and row[1]:
                verified, msg = self.verify_payment_with_fampay(row[1])
                if verified is False:
                    conn.close()
                    return False, f"FamPay verification failed: {msg}"
                elif verified is None:
                    # API error - log but proceed? We'll proceed but warn
                    logger.warning(f"FamPay verification skipped: {msg}")
            
            c.execute('UPDATE payments SET status = "approved", updated_at = CURRENT_TIMESTAMP WHERE payment_id = ?', (payment_id,))
            c.execute('SELECT user_id, plan_id FROM payments WHERE payment_id = ?', (payment_id,))
            payment = c.fetchone()
            if payment:
                user_id, plan_id = payment
                plan = self.get_plan(plan_id)
                if plan:
                    expiry = (datetime.now() + timedelta(days=plan['validity_days'])).isoformat()
                    c.execute('UPDATE users SET subscription_plan_id = ?, subscription_expiry = ? WHERE user_id = ?',
                             (plan_id, expiry, user_id))
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            logger.error(f"Approve payment error: {e}")
            conn.close()
            return False, str(e)
    
    def reject_payment(self, payment_id, reason=""):
        conn = self.get_conn()
        c = conn.cursor()
        try:
            c.execute('SELECT status FROM payments WHERE payment_id = ?', (payment_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                return False, "Payment not found"
            if row[0] != 'pending':
                conn.close()
                return False, f"Payment already {row[0]}"
            c.execute('UPDATE payments SET status = "rejected", admin_comment = ?, updated_at = CURRENT_TIMESTAMP WHERE payment_id = ?',
                     (reason, payment_id))
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            logger.error(f"Reject payment error: {e}")
            conn.close()
            return False, str(e)
    
    def get_setting(self, key):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('SELECT setting_value FROM settings WHERE setting_key = ?', (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else ''
    
    def set_setting(self, key, value):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
    
    def get_stats(self):
        conn = self.get_conn()
        c = conn.cursor()
        stats = {}
        c.execute('SELECT COUNT(*) FROM users')
        stats['total_users'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM payments WHERE status="approved"')
        stats['total_payments'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM payments WHERE status="pending"')
        stats['pending'] = c.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('SELECT COALESCE(SUM(amount),0) FROM payments WHERE status="approved" AND date(created_at)=?', (today,))
        stats['today_earning'] = float(c.fetchone()[0])
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        c.execute('SELECT COALESCE(SUM(amount),0) FROM payments WHERE status="approved" AND date(created_at)=?', (yesterday,))
        stats['yesterday_earning'] = float(c.fetchone()[0])
        conn.close()
        return stats

# ==================== QR CODE ====================
def generate_qr(upi_id, amount=0, payee_name="Premium Bot"):
    if not upi_id:
        return None
    upi_string = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount}&cu=INR"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(upi_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# ==================== BOT ====================
db = Database()
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

WELCOME_IMAGE = db.get_setting('welcome_image')
WELCOME_VIDEO = db.get_setting('welcome_video')
WELCOME_TEXT = db.get_setting('welcome_text')
BOT_NAME = db.get_setting('bot_name')
UPI_ID = db.get_setting('upi_id')
QR_CODE = db.get_setting('qr_code')

user_data = {}
bot_running = True

def load_admins():
    global ADMIN_IDS
    conn = db.get_conn()
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE is_admin = 1')
    rows = c.fetchall()
    conn.close()
    ADMIN_IDS = [row[0] for row in rows]
    return ADMIN_IDS

load_admins()

def is_admin(user_id):
    return db.is_admin(user_id)

def safe_send(chat_id, text, **kwargs):
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except:
        return None

def safe_photo(chat_id, photo, caption='', **kwargs):
    try:
        return bot.send_photo(chat_id, photo, caption=caption, **kwargs)
    except:
        return None

def safe_video(chat_id, video, caption='', **kwargs):
    try:
        return bot.send_video(chat_id, video, caption=caption, **kwargs)
    except:
        return None

# ---------- BOT HANDLERS ----------
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    user_id = msg.from_user.id
    db.add_user(user_id, msg.from_user.username or '', msg.from_user.first_name or '', msg.from_user.last_name or '')
    load_admins()
    if not ADMIN_IDS:
        db.set_admin(user_id)
        load_admins()
        bot.send_message(user_id, "✅ You are the first ADMIN! Use /admin for panel.")
    if user_id in ADMIN_IDS:
        db.set_admin(user_id)
        load_admins()
    for admin_id in ADMIN_IDS:
        if admin_id != user_id:
            try:
                bot.send_message(admin_id, f"👤 New user started bot!\n\nID: {user_id}\nName: {msg.from_user.first_name}\nUsername: @{msg.from_user.username or 'N/A'}")
            except:
                pass
    if WELCOME_VIDEO:
        caption = f"<b>{BOT_NAME}</b>\n\n{WELCOME_TEXT}"
        safe_video(user_id, WELCOME_VIDEO, caption=caption)
    elif WELCOME_IMAGE:
        caption = f"<b>{BOT_NAME}</b>\n\n{WELCOME_TEXT}"
        safe_photo(user_id, WELCOME_IMAGE, caption=caption)
    else:
        text = f"<b>{BOT_NAME}</b>\n\n{WELCOME_TEXT}"
        safe_send(user_id, text)
    safe_send(user_id, "👇 Choose a plan below 💎")
    plans = db.get_all_plans()
    if plans:
        kb = types.InlineKeyboardMarkup(row_width=1)
        for p in plans:
            label = f"{p['name']}  |  ₹{int(p['price'])} / {p['validity_days']}d"
            kb.add(types.InlineKeyboardButton(label, callback_data=f"view_plan_{p['plan_id']}"))
        safe_send(user_id, "📋 Available Plans:", reply_markup=kb)
    else:
        safe_send(user_id, "❌ No plans available yet.")

@bot.message_handler(commands=['setme'])
def setme_cmd(msg):
    user_id = msg.from_user.id
    if db.is_admin(user_id):
        bot.reply_to(msg, "✅ You are already an admin!")
        return
    db.set_admin(user_id)
    load_admins()
    bot.reply_to(msg, "👑 You are now an admin! Use /admin to access the admin panel.")

@bot.message_handler(commands=['admin'])
def admin_cmd(msg):
    user_id = msg.from_user.id
    if not is_admin(user_id):
        safe_send(user_id, "❌ Unauthorized access!")
        return
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.row(
        types.InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 Users", callback_data="admin_users")
    )
    kb.row(
        types.InlineKeyboardButton("📋 Plans", callback_data="admin_plans"),
        types.InlineKeyboardButton("💳 Payments", callback_data="admin_payments")
    )
    kb.row(
        types.InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
        types.InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    )
    if user_id == ADMIN_IDS[0] if ADMIN_IDS else False:
        kb.add(types.InlineKeyboardButton("👑 Admin Management", callback_data="admin_management"))
    kb.add(types.InlineKeyboardButton("📤 Export DB", callback_data="admin_export"))
    kb.add(types.InlineKeyboardButton("📥 Import DB", callback_data="admin_import"))
    safe_send(user_id, f"<b>⚙️ Admin Panel</b>\n\nWelcome {BOT_NAME} admin!", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(call):
    user_id = call.from_user.id
    data = call.data
    try:
        # ---------- USER FLOW ----------
        if data.startswith("view_plan_"):
            plan_id = int(data.split("_")[2])
            plan = db.get_plan(plan_id)
            if plan:
                media = db.get_plan_media(plan_id)
                photos, videos = [], []
                for m in media[:10]:
                    if m['type'] == 'photo':
                        photos.append(m['file_id'])
                    elif m['type'] == 'video':
                        videos.append(m['file_id'])
                if photos:
                    try:
                        media_group = []
                        for photo in photos[:10]:
                            media_group.append(types.InputMediaPhoto(photo))
                        bot.send_media_group(user_id, media_group)
                    except:
                        for photo in photos:
                            safe_photo(user_id, photo)
                if videos:
                    for video in videos:
                        safe_video(user_id, video)
                content_text = plan.get('description', f"{len(media)} items")
                text = f"✨ <b>Premium Plan Selected</b> ✨\n"
                text += "━━━━━━━━━━━━━━\n"
                text += f"🎬 Content approx: {content_text}\n"
                text += f"📦 Plan: {plan['name']}\n"
                text += f"💰 Price: ₹{int(plan['price'])}\n"
                text += f"⏳ Validity: {plan['validity_days']}d\n"
                text += "━━━━━━━━━━━━━━\n"
                text += "👇 Tap below to generate your QR with this exact amount."
                kb = types.InlineKeyboardMarkup(row_width=1)
                kb.add(types.InlineKeyboardButton("🔊 PAY NOW", callback_data=f"pay_now_{plan_id}"))
                kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_main"))
                safe_send(user_id, text, reply_markup=kb)
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Plan not found!")
        
        elif data.startswith("pay_now_"):
            plan_id = int(data.split("_")[2])
            plan = db.get_plan(plan_id)
            if plan:
                user_data[user_id] = {'buying_plan': plan_id}
                upi = db.get_setting('upi_id')
                if not upi:
                    safe_send(user_id, "❌ UPI ID not configured by admin.")
                    return
                amount = int(plan['price'])
                qr_img = generate_qr(upi, amount, BOT_NAME)
                if qr_img:
                    try:
                        sent_msg = bot.send_photo(user_id, qr_img, caption=f"💳 <b>Scan & Pay</b>\n"
                        f"Plan: {plan['name']}\nAmount: ₹{amount}\nUPI: {upi}\n\n"
                        f"📝 After payment, send screenshot with UTR/Order ID in caption.",
                        reply_markup=types.InlineKeyboardMarkup().add(
                        types.InlineKeyboardButton("📸 Verify Payment", callback_data=f"verify_payment_{plan_id}"),
                        types.InlineKeyboardButton("🔙 Back", callback_data="back_main")))
                        if sent_msg and sent_msg.photo:
                            db.set_setting('qr_code', sent_msg.photo[-1].file_id)
                    except:
                        safe_send(user_id, "❌ QR generation failed.")
                else:
                    safe_send(user_id, "❌ UPI ID invalid.")
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.answer_callback_query(call.id, "Plan not found!")
        
        elif data.startswith("verify_payment_"):
            plan_id = int(data.split("_")[2])
            plan = db.get_plan(plan_id)
            if plan:
                user_data[user_id] = {'screenshot_plan': plan_id}
                text = f"📸 Send payment screenshot for {plan['name']} (₹{plan['price']})\n"
                text += "📝 Caption mein UTR / Order ID zaroor likhein (FamPay verification ke liye)"
                kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="back_main"))
                safe_send(user_id, text, reply_markup=kb)
                bot.answer_callback_query(call.id, "Send screenshot now with UTR in caption!")
            else:
                bot.answer_callback_query(call.id, "Plan not found!")
        
        elif data == "back_main":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start_cmd(call.message)
        
        # ---------- ADMIN PANEL ----------
        elif data == "admin_stats":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            s = db.get_stats()
            text = f"<b>📊 Statistics</b>\n\n"
            text += f"👥 Total Users: {s['total_users']}\n"
            text += f"💰 Total Payments: {s['total_payments']}\n"
            text += f"🕐 Pending Payments: {s['pending']}\n"
            text += f"📈 Today's Earnings: ₹{s['today_earning']:.2f}\n"
            text += f"📉 Yesterday's Earnings: ₹{s['yesterday_earning']:.2f}"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_users":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            users = db.get_all_users()
            text = f"<b>👥 Users</b> ({len(users)})\n\n"
            for u in users[:20]:
                text += f"👤 {u.get('first_name', 'Unknown')} (@{u.get('username', 'N/A')}) - {'✅' if u.get('is_admin') else '❌'}\n"
            if len(users) > 20:
                text += f"\n... and {len(users)-20} more"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_plans":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            plans = db.get_all_plans()
            text = "📋 <b>Plans</b>\n\n"
            if plans:
                for p in plans:
                    text += f"📦 {p['name']} - ₹{p['price']} / {p['validity_days']} days\n"
            else:
                text += "No plans yet."
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(types.InlineKeyboardButton("➕ Add Plan", callback_data="admin_add_plan"))
            kb.add(types.InlineKeyboardButton("🗑️ Delete Plan", callback_data="admin_delete_plan_list"))
            kb.add(types.InlineKeyboardButton("✏️ Edit Plan", callback_data="admin_edit_plan_list"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_payments":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            pending = db.get_pending_payments()
            text = f"<b>💳 Pending Payments</b> ({len(pending)})\n\n"
            if pending:
                for p in pending:
                    text += f"👤 {p.get('first_name', 'Unknown')} - ₹{p['amount']} - Plan: {p.get('plan_name', 'N/A')}\n"
                    if p.get('order_id'):
                        text += f"   🆔 Order: {p['order_id']}\n"
            else:
                text += "No pending payments."
            kb = types.InlineKeyboardMarkup(row_width=1)
            for p in pending[:10]:
                kb.add(types.InlineKeyboardButton(f"📌 {p.get('first_name', 'Unknown')} - ₹{p['amount']}", callback_data=f"pview_{p['payment_id']}"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data.startswith("pview_"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            pid = int(data.split("_")[1])
            payment = db.get_payment(pid)
            if payment:
                user = db.get_user(payment['user_id'])
                plan = db.get_plan(payment['plan_id'])
                text = f"<b>💳 Payment #{pid}</b>\n\n"
                text += f"👤 User: {user.get('first_name', 'Unknown')}\n"
                text += f"📋 Plan: {plan['name'] if plan else 'Unknown'}\n"
                text += f"💰 Amount: ₹{payment['amount']}\n"
                text += f"🆔 Order ID: {payment.get('order_id', 'N/A')}\n"
                text += f"📅 Date: {payment['created_at'][:16]}\n"
                text += f"📌 Status: <b>{payment['status'].upper()}</b>"
                kb = types.InlineKeyboardMarkup(row_width=2)
                if payment['status'] == 'pending':
                    kb.row(
                        types.InlineKeyboardButton("✅ Approve (with FamPay)", callback_data=f"approve_{pid}"),
                        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{pid}")
                    )
                    kb.add(types.InlineKeyboardButton("⏩ Approve (Skip Verify)", callback_data=f"approve_skip_{pid}"))
                kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_payments"))
                safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
            else:
                bot.answer_callback_query(call.id, "Payment not found!")
        
        elif data.startswith("approve_"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            pid = int(data.split("_")[1])
            skip_verify = data.startswith("approve_skip_")
            success, msg = db.approve_payment(pid, skip_verify=skip_verify)
            if success:
                bot.answer_callback_query(call.id, "✅ Payment approved!")
                # Notify user
                payment = db.get_payment(pid)
                if payment:
                    user = db.get_user(payment['user_id'])
                    plan = db.get_plan(payment['plan_id'])
                    if user and plan:
                        link = plan.get('channel_link', '')
                        text = f"✅ <b>Payment Approved!</b>\n\n📦 Plan: {plan['name']}\n💰 Amount: ₹{payment['amount']}\n📅 Validity: {plan['validity_days']} days"
                        if link:
                            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔗 Access Content", url=link))
                            bot.send_message(payment['user_id'], text, reply_markup=kb)
                        else:
                            bot.send_message(payment['user_id'], text)
            else:
                bot.answer_callback_query(call.id, f"❌ {msg}")
            # Refresh payments list
            data = "admin_payments"
            handle_cb(call)
        
        elif data.startswith("reject_"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            pid = int(data.split("_")[1])
            user_data[user_id] = {'reject_payment': pid}
            text = "📝 Send rejection reason:"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_payments"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_settings":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            text = f"<b>⚙️ Settings</b>\n\n"
            text += f"🤖 Bot Name: {BOT_NAME}\n"
            text += f"💰 UPI ID: {UPI_ID or 'Not set'}\n"
            text += f"🔑 FamPay API: {'✅ Set' if FAMPAY_API_KEY != 'YOUR_API_KEY_HERE' else '❌ Not set'}\n"
            text += f"🖼️ Welcome Image: {'✅' if WELCOME_IMAGE else '❌'}\n"
            text += f"🎬 Welcome Video: {'✅' if WELCOME_VIDEO else '❌'}\n"
            text += f"📝 Welcome Text: {WELCOME_TEXT[:30]}..."
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(types.InlineKeyboardButton("✏️ Bot Name", callback_data="set_bot_name"))
            kb.add(types.InlineKeyboardButton("💰 UPI ID", callback_data="set_upi_id"))
            kb.add(types.InlineKeyboardButton("🔑 FamPay API", callback_data="set_fampay_api"))
            kb.add(types.InlineKeyboardButton("📝 Welcome Text", callback_data="set_welcome_text"))
            kb.add(types.InlineKeyboardButton("🖼️ Welcome Image", callback_data="set_welcome_image"))
            kb.add(types.InlineKeyboardButton("🎬 Welcome Video", callback_data="set_welcome_video"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_broadcast":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'broadcast': True}
            text = "📢 <b>Send Broadcast</b>\n\nSend the message you want to broadcast to all users."
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_management":
            if not is_admin(user_id) or user_id != ADMIN_IDS[0]:
                bot.answer_callback_query(call.id, "Only main admin can manage admins!")
                return
            admins = db.get_admins()
            text = "👑 <b>Admin Management</b>\n\n"
            for i, a in enumerate(admins, 1):
                text += f"{i}. {a[1] or 'Unknown'} - {'⭐ MAIN' if i == 1 else ''}\n"
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(types.InlineKeyboardButton("➕ Add Admin", callback_data="admin_add_admin"))
            if len(admins) > 1:
                kb.add(types.InlineKeyboardButton("❌ Remove Admin", callback_data="admin_remove_admin_list"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_add_admin":
            if not is_admin(user_id) or user_id != ADMIN_IDS[0]:
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'add_admin': True}
            text = "➕ Send the Telegram User ID of the new admin."
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_management"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_remove_admin_list":
            if not is_admin(user_id) or user_id != ADMIN_IDS[0]:
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            admins = db.get_admins()
            if len(admins) <= 1:
                bot.answer_callback_query(call.id, "Cannot remove last admin!")
                return
            text = "❌ Select admin to remove:"
            kb = types.InlineKeyboardMarkup(row_width=1)
            for a in admins:
                if a[0] != user_id:
                    kb.add(types.InlineKeyboardButton(f"❌ {a[1] or 'Unknown'}", callback_data=f"admin_remove_{a[0]}"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_management"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data.startswith("admin_remove_"):
            if not is_admin(user_id) or user_id != ADMIN_IDS[0]:
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            remove_id = int(data.split("_")[2])
            if remove_id == user_id:
                bot.answer_callback_query(call.id, "Cannot remove yourself!")
                return
            db.remove_admin(remove_id)
            load_admins()
            bot.answer_callback_query(call.id, "✅ Admin removed!")
            data = "admin_management"
            handle_cb(call)
        
        elif data == "admin_export":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            kb = types.InlineKeyboardMarkup(row_width=2)
            kb.add(types.InlineKeyboardButton("📤 Export .db", callback_data="export_db"))
            kb.add(types.InlineKeyboardButton("📤 Export .sql", callback_data="export_sql"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, "📤 Export Database (Plans + Media)", reply_markup=kb)
        
        elif data == "admin_import":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'import_db': True}
            text = "📥 Send a `.db` or `.sql` file to import."
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel_back"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_panel_back":
            admin_cmd(call.message)
        
        elif data.startswith("export_db"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            try:
                temp_path = "temp_plans_export.db"
                conn = sqlite3.connect(temp_path)
                c = conn.cursor()
                c.execute('''CREATE TABLE plans (
                    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, price REAL, validity_days INTEGER,
                    channel_link TEXT, description TEXT,
                    media_json TEXT, is_active INTEGER, created_at TEXT
                )''')
                main_conn = db.get_conn()
                main_c = main_conn.cursor()
                main_c.execute('SELECT * FROM plans')
                rows = main_c.fetchall()
                main_conn.close()
                for row in rows:
                    c.execute('INSERT INTO plans VALUES (?,?,?,?,?,?,?,?,?)', row)
                conn.commit()
                conn.close()
                with open(temp_path, 'rb') as f:
                    bot.send_document(user_id, f, caption="📤 Plans exported as .db")
                os.remove(temp_path)
            except Exception as e:
                bot.send_message(user_id, f"❌ Export failed: {e}")
        
        elif data.startswith("export_sql"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            try:
                conn = db.get_conn()
                c = conn.cursor()
                c.execute('SELECT * FROM plans')
                rows = c.fetchall()
                conn.close()
                if not rows:
                    bot.send_message(user_id, "No plans to export.")
                    return
                dump = "-- Plans Export\n"
                dump += "BEGIN TRANSACTION;\n"
                dump += '''CREATE TABLE plans (
                    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT, price REAL, validity_days INTEGER,
                    channel_link TEXT, description TEXT,
                    media_json TEXT, is_active INTEGER, created_at TEXT
                );\n'''
                for row in rows:
                    plan_id, name, price, validity, link, descr, media, active, created = row
                    name = name.replace("'", "''")
                    descr = (descr or "").replace("'", "''")
                    link = (link or "").replace("'", "''")
                    media = (media or "[]").replace("'", "''")
                    dump += f"INSERT INTO plans VALUES ({plan_id}, '{name}', {price}, {validity}, '{link}', '{descr}', '{media}', {active}, '{created}');\n"
                dump += "COMMIT;\n"
                sql_bytes = BytesIO(dump.encode('utf-8'))
                sql_bytes.seek(0)
                bot.send_document(user_id, sql_bytes, visible_file_name="plans_export.sql", caption="📤 Plans exported as .sql")
            except Exception as e:
                bot.send_message(user_id, f"❌ Export failed: {e}")
        
        elif data == "set_bot_name":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'setting': 'bot_name'}
            text = "Send new bot name:"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_settings"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "set_upi_id":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'setting': 'upi_id'}
            text = "Send new UPI ID:"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_settings"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "set_fampay_api":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'setting': 'fampay_api'}
            text = "Send new FamPay API Key:"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_settings"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "set_welcome_text":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'setting': 'welcome_text'}
            text = "Send new welcome text:"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_settings"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "set_welcome_image":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'setting': 'welcome_image'}
            text = "Send a photo to set as welcome image."
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_settings"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "set_welcome_video":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'setting': 'welcome_video'}
            text = "Send a video to set as welcome video."
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_settings"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data == "admin_edit_plan_list":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            plans = db.get_all_plans()
            text = "📝 Select plan to edit:"
            kb = types.InlineKeyboardMarkup(row_width=1)
            for p in plans:
                kb.add(types.InlineKeyboardButton(f"✏️ {p['name']}", callback_data=f"edit_plan_{p['plan_id']}"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_plans"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data.startswith("edit_plan_"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            plan_id = int(data.split("_")[2])
            plan = db.get_plan(plan_id)
            if not plan:
                bot.answer_callback_query(call.id, "Plan not found!")
                return
            user_data[user_id] = {'edit_plan': plan_id}
            text = f"✏️ Editing {plan['name']}\nCurrent details:\nPrice: ₹{plan['price']}\nValidity: {plan['validity_days']} days\nDescription: {plan.get('description', '')}\n\nSend new name (or /skip to keep current):"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_plans"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
            user_data[user_id]['edit_step'] = 'name'
        
        elif data == "admin_delete_plan_list":
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            plans = db.get_all_plans()
            text = "🗑️ Select plan to delete:"
            kb = types.InlineKeyboardMarkup(row_width=1)
            for p in plans:
                kb.add(types.InlineKeyboardButton(f"❌ {p['name']}", callback_data=f"delete_plan_{p['plan_id']}"))
            kb.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_plans"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
        
        elif data.startswith("delete_plan_"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            plan_id = int(data.split("_")[2])
            db.delete_plan(plan_id)
            bot.answer_callback_query(call.id, "✅ Plan deleted!")
            data = "admin_plans"
            handle_cb(call)
        
        elif data.startswith("admin_add_plan"):
            if not is_admin(user_id):
                bot.answer_callback_query(call.id, "Unauthorized!")
                return
            user_data[user_id] = {'add_plan': True}
            text = "➕ Add new plan:\nSend plan name:"
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Cancel", callback_data="admin_plans"))
            safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=kb)
            user_data[user_id]['step'] = 'name'

    except Exception as e:
        logger.error(f"Callback error: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Error occurred!")
        except:
            pass

def safe_edit(chat_id, msg_id, text, **kwargs):
    try:
        bot.edit_message_text(text, chat_id, msg_id, **kwargs)
    except:
        pass

# ---------- TEXT HANDLERS ----------
@bot.message_handler(func=lambda m: m.text and m.text.startswith('/skip') and m.from_user.id in user_data and 'edit_plan' in user_data[m.from_user.id])
def skip_edit(msg):
    user_id = msg.from_user.id
    if 'edit_plan' in user_data[user_id]:
        plan_id = user_data[user_id]['edit_plan']
        plan = db.get_plan(plan_id)
        if plan:
            step = user_data[user_id].get('edit_step')
            if step == 'name':
                user_data[user_id]['edit_step'] = 'price'
                bot.reply_to(msg, f"OK, keeping name as {plan['name']}. Send new price (or /skip):")
            elif step == 'price':
                user_data[user_id]['edit_step'] = 'validity'
                bot.reply_to(msg, f"OK, keeping price ₹{plan['price']}. Send new validity in days (or /skip):")
            elif step == 'validity':
                user_data[user_id]['edit_step'] = 'description'
                bot.reply_to(msg, f"OK, keeping validity {plan['validity_days']} days. Send new description (or /skip):")
            elif step == 'description':
                del user_data[user_id]
                bot.reply_to(msg, "✅ Plan updated successfully!")
                admin_cmd(msg)
        else:
            del user_data[user_id]
            bot.reply_to(msg, "❌ Plan not found.")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(msg):
    user_id = msg.from_user.id
    text = msg.text.strip()

    # ---- REJECT PAYMENT REASON ----
    if user_id in user_data and 'reject_payment' in user_data[user_id]:
        pid = user_data[user_id]['reject_payment']
        db.reject_payment(pid, text)
        bot.reply_to(msg, "✅ Payment rejected!")
        # Notify user
        payment = db.get_payment(pid)
        if payment:
            user = db.get_user(payment['user_id'])
            plan = db.get_plan(payment['plan_id'])
            if user and plan:
                bot.send_message(payment['user_id'], f"❌ Payment Rejected\nPlan: {plan['name']}\nReason: {text}")
        del user_data[user_id]
        return

    # ---- ADD ADMIN ----
    if user_id in user_data and user_data[user_id].get('add_admin'):
        try:
            new_id = int(text)
            if db.is_admin(new_id):
                bot.reply_to(msg, "❌ This user is already an admin.")
            else:
                db.set_admin(new_id)
                load_admins()
                bot.reply_to(msg, f"✅ User {new_id} is now an admin.")
        except:
            bot.reply_to(msg, "❌ Invalid User ID. Send a number.")
        del user_data[user_id]
        return

    # ---- EDIT PLAN ----
    if user_id in user_data and 'edit_plan' in user_data[user_id]:
        plan_id = user_data[user_id]['edit_plan']
        step = user_data[user_id].get('edit_step')
        if step == 'name':
            db.update_plan(plan_id, name=text)
            user_data[user_id]['edit_step'] = 'price'
            bot.reply_to(msg, f"✅ Name updated to: {text}. Send new price (or /skip):")
        elif step == 'price':
            try:
                price = float(text)
                db.update_plan(plan_id, price=price)
                user_data[user_id]['edit_step'] = 'validity'
                bot.reply_to(msg, f"✅ Price updated to ₹{price}. Send new validity in days (or /skip):")
            except:
                bot.reply_to(msg, "❌ Invalid price. Send a number.")
        elif step == 'validity':
            try:
                days = int(text)
                db.update_plan(plan_id, validity_days=days)
                user_data[user_id]['edit_step'] = 'description'
                bot.reply_to(msg, f"✅ Validity updated to {days} days. Send new description (or /skip):")
            except:
                bot.reply_to(msg, "❌ Invalid days. Send a number.")
        elif step == 'description':
            db.update_plan(plan_id, description=text)
            del user_data[user_id]
            bot.reply_to(msg, "✅ Plan updated successfully!")
            admin_cmd(msg)
        return

    # ---- ADD PLAN ----
    if user_id in user_data and user_data[user_id].get('add_plan'):
        step = user_data[user_id].get('step')
        if step == 'name':
            user_data[user_id]['pname'] = text
            user_data[user_id]['step'] = 'price'
            bot.reply_to(msg, "Send plan price (₹):")
        elif step == 'price':
            try:
                price = float(text)
                user_data[user_id]['pprice'] = price
                user_data[user_id]['step'] = 'validity'
                bot.reply_to(msg, "Send validity in days:")
            except:
                bot.reply_to(msg, "❌ Invalid price.")
        elif step == 'validity':
            try:
                days = int(text)
                user_data[user_id]['pvalidity'] = days
                user_data[user_id]['step'] = 'link'
                bot.reply_to(msg, "Send channel link (optional, send /skip to skip):")
            except:
                bot.reply_to(msg, "❌ Invalid days.")
        elif step == 'link':
            if text == '/skip':
                link = ''
            else:
                link = text
            user_data[user_id]['plink'] = link
            user_data[user_id]['step'] = 'desc'
            bot.reply_to(msg, "Send description (optional, send /skip to skip):")
        elif step == 'desc':
            desc = '' if text == '/skip' else text
            name = user_data[user_id]['pname']
            price = user_data[user_id]['pprice']
            days = user_data[user_id]['pvalidity']
            link = user_data[user_id]['plink']
            db.add_plan(name, price, days, link, desc)
            del user_data[user_id]
            bot.reply_to(msg, f"✅ Plan '{name}' added successfully!")
            admin_cmd(msg)
        return

    # ---- SETTINGS ----
    if user_id in user_data and 'setting' in user_data[user_id]:
        key = user_data[user_id]['setting']
        if key == 'bot_name':
            db.set_setting('bot_name', text)
            global BOT_NAME
            BOT_NAME = text
            bot.reply_to(msg, f"✅ Bot name updated to: {text}")
        elif key == 'upi_id':
            db.set_setting('upi_id', text)
            global UPI_ID
            UPI_ID = text
            bot.reply_to(msg, "✅ UPI ID updated.")
        elif key == 'fampay_api':
            global FAMPAY_API_KEY
            FAMPAY_API_KEY = text
            bot.reply_to(msg, "✅ FamPay API Key updated.")
        elif key == 'welcome_text':
            db.set_setting('welcome_text', text)
            global WELCOME_TEXT
            WELCOME_TEXT = text
            bot.reply_to(msg, "✅ Welcome text updated.")
        del user_data[user_id]
        return

    # ---- BROADCAST ----
    if user_id in user_data and user_data[user_id].get('broadcast'):
        users = db.get_all_users()
        sent = 0
        for u in users:
            try:
                bot.send_message(u['user_id'], text)
                sent += 1
                time.sleep(0.05)
            except:
                pass
        bot.reply_to(msg, f"✅ Broadcast sent to {sent} users!")
        del user_data[user_id]
        return

    # ---- IMPORT DB ----
    if user_id in user_data and user_data[user_id].get('import_db'):
        bot.reply_to(msg, "❌ Please send a file (document) with .db or .sql extension.")
        return

# ---------- DOCUMENT HANDLER ----------
@bot.message_handler(content_types=['document'])
def handle_document(msg):
    user_id = msg.from_user.id
    if user_id in user_data and user_data[user_id].get('import_db'):
        file = msg.document
        file_name = file.file_name.lower()
        if not (file_name.endswith('.db') or file_name.endswith('.sql')):
            bot.reply_to(msg, "❌ Please send a .db or .sql file.")
            return
        try:
            file_info = bot.get_file(file.file_id)
            downloaded = bot.download_file(file_info.file_path)
            if file_name.endswith('.db'):
                with open(DATABASE_PATH, 'wb') as f:
                    f.write(downloaded)
                global db
                db = Database()
                load_admins()
                bot.reply_to(msg, "✅ Database imported successfully from .db file!")
            elif file_name.endswith('.sql'):
                sql = downloaded.decode('utf-8')
                conn = db.get_conn()
                c = conn.cursor()
                queries = sql.split(';')
                executed = 0
                for q in queries:
                    q = q.strip()
                    if q:
                        try:
                            c.execute(q)
                            executed += 1
                        except:
                            pass
                conn.commit()
                conn.close()
                db = Database()
                load_admins()
                bot.reply_to(msg, f"✅ SQL imported successfully! {executed} queries executed.")
            del user_data[user_id]
        except Exception as e:
            bot.reply_to(msg, f"❌ Import failed: {e}")
        return

# ---------- PHOTO HANDLER ----------
@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    user_id = msg.from_user.id
    file_id = msg.photo[-1].file_id
    caption = msg.caption or ""

    # For welcome image setting
    if user_id in user_data and user_data[user_id].get('setting') == 'welcome_image':
        db.set_setting('welcome_image', file_id)
        global WELCOME_IMAGE
        WELCOME_IMAGE = file_id
        bot.reply_to(msg, "✅ Welcome image updated!")
        del user_data[user_id]
        return

    # For payment screenshot
    if user_id in user_data and 'screenshot_plan' in user_data[user_id]:
        plan_id = user_data[user_id]['screenshot_plan']
        plan = db.get_plan(plan_id)
        if plan:
            # Extract order_id from caption (UTR/Order ID)
            order_id = caption.strip() if caption else ''
            pid = db.add_payment(user_id, plan_id, plan['price'], file_id, order_id)
            bot.reply_to(msg, f"✅ Payment screenshot received!\n🆔 Order ID: {order_id or 'Not provided'}\nAdmin will review shortly.")
            # Notify admins
            for admin in ADMIN_IDS:
                try:
                    text = f"💳 New Payment #{pid}\nUser: {msg.from_user.first_name}\nPlan: {plan['name']}\nAmount: ₹{plan['price']}\n🆔 Order ID: {order_id or 'N/A'}"
                    bot.send_photo(admin, file_id, caption=text)
                except:
                    pass
            del user_data[user_id]
        return

# ---------- VIDEO HANDLER ----------
@bot.message_handler(content_types=['video'])
def handle_video(msg):
    user_id = msg.from_user.id
    file_id = msg.video.file_id
    if user_id in user_data and user_data[user_id].get('setting') == 'welcome_video':
        db.set_setting('welcome_video', file_id)
        global WELCOME_VIDEO
        WELCOME_VIDEO = file_id
        bot.reply_to(msg, "✅ Welcome video updated!")
        del user_data[user_id]
        return

# ==================== FLASK WEB DASHBOARD ====================
app = Flask(__name__)

@app.route('/')
def stats_dashboard():
    stats = db.get_stats()
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bot Stats</title>
        <style>
            * { margin:0; padding:0; box-sizing:border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0d1117; color: #c9d1d9; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .container { max-width: 800px; width: 100%; padding: 20px; }
            .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
            .card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 24px; text-align: center; transition: 0.3s; }
            .card:hover { border-color: #58a6ff; transform: translateY(-4px); }
            .card .number { font-size: 36px; font-weight: 700; color: #58a6ff; margin-bottom: 8px; }
            .card .label { font-size: 14px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; }
            .card.today .number { color: #3fb950; }
            .card.yesterday .number { color: #f0883e; }
            .card.pending .number { color: #f85149; }
            .card.total .number { color: #d2a8ff; }
            .title { text-align: center; margin-bottom: 30px; font-size: 24px; font-weight: 600; color: #f0f6fc; }
            .footer { text-align: center; margin-top: 30px; font-size: 12px; color: #8b949e; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="title">📊 Bot Stats Dashboard</div>
            <div class="card-grid">
                <div class="card">
                    <div class="number">{{ total_users }}</div>
                    <div class="label">Total Users</div>
                </div>
                <div class="card today">
                    <div class="number">₹{{ today_earning|round(2) }}</div>
                    <div class="label">Today's Earnings</div>
                </div>
                <div class="card yesterday">
                    <div class="number">₹{{ yesterday_earning|round(2) }}</div>
                    <div class="label">Yesterday's Earnings</div>
                </div>
                <div class="card pending">
                    <div class="number">{{ pending_payments }}</div>
                    <div class="label">Pending Payments</div>
                </div>
                <div class="card total">
                    <div class="number">₹{{ total_payments|round(2) }}</div>
                    <div class="label">Total Payments (Approved)</div>
                </div>
            </div>
            <div class="footer">Updated in real-time • Bot by @{{ bot_username }}</div>
        </div>
    </body>
    </html>
    '''
    bot_username = os.getenv('BOT_USERNAME', 'YourBot')
    return render_template_string(html,
                                  total_users=stats['total_users'],
                                  today_earning=stats['today_earning'],
                                  yesterday_earning=stats['yesterday_earning'],
                                  pending_payments=stats['pending'],
                                  total_payments=stats['total_payments'],
                                  bot_username=bot_username)

# ==================== BOT THREAD ====================
def run_bot():
    while bot_running:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            if bot_running:
                time.sleep(5)

# Start bot thread
thread = threading.Thread(target=run_bot, daemon=True)
thread.start()
logger.info("🤖 Bot polling thread started.")

# ==================== MAIN ====================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=False)