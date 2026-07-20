# ============================================================================
#  bot.py – Garena Bind Tool Bot (Single‑File Version)
# ============================================================================
#  Replace these with your actual values:
BOT_TOKEN = "8620265232:AAGFCdzR83BsftHaZDHik5yqvQQtqKQjw1k"          # from @BotFather
ADMIN_ID = 7709767483                  # your Telegram user ID (integer)

# ============================================================================
#  IMPORTS
# ============================================================================
import os
import sys
import json
import time
import urllib.parse
import base64
import hashlib
import urllib3
import sqlite3
import logging
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, Any, List, Tuple

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================================
#  PROTOBUF DEFINITIONS (embedded – no external files needed)
# ============================================================================
# We embed the full generated protobuf classes for MajorLoginReq and MajorLoginRes.
# This avoids the need for separate .py files.

# ---------- MajoRLogin_pb2 ----------
import google.protobuf
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()

DESCRIPTOR_MAJORLOGIN = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginReq.proto\"\xfa\n\n\nMajorLogin\x12\x12\n\nevent_time\x18\x03 \x01(\t\x12\x11\n\tgame_name\x18\x04 \x01(\t\x12\x13\n\x0bplatform_id\x18\x05 \x01(\x05\x12\x16\n\x0e\x63lient_version\x18\x07 \x01(\t\x12\x17\n\x0fsystem_software\x18\x08 \x01(\t\x12\x17\n\x0fsystem_hardware\x18\t \x01(\t\x12\x18\n\x10telecom_operator\x18\n \x01(\t\x12\x14\n\x0cnetwork_type\x18\x0b \x01(\t\x12\x14\n\x0cscreen_width\x18\x0c \x01(\r\x12\x15\n\rscreen_height\x18\r \x01(\r\x12\x12\n\nscreen_dpi\x18\x0e \x01(\t\x12\x19\n\x11processor_details\x18\x0f \x01(\t\x12\x0e\n\x06memory\x18\x10 \x01(\r\x12\x14\n\x0cgpu_renderer\x18\x11 \x01(\t\x12\x13\n\x0bgpu_version\x18\x12 \x01(\t\x12\x18\n\x10unique_device_id\x18\x13 \x01(\t\x12\x11\n\tclient_ip\x18\x14 \x01(\t\x12\x10\n\x08language\x18\x15 \x01(\t\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0b\x64\x65vice_type\x18\x18 \x01(\t\x12\'\n\x10memory_available\x18\x19 \x01(\x0b\x32\r.GameSecurity\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x1d \x01(\t\x12\x17\n\x0fplatform_sdk_id\x18\x1e \x01(\x05\x12\x1a\n\x12network_operator_a\x18) \x01(\t\x12\x16\n\x0enetwork_type_a\x18* \x01(\t\x12\x1c\n\x14\x63lient_using_version\x18\x39 \x01(\t\x12\x1e\n\x16\x65xternal_storage_total\x18< \x01(\x05\x12\"\n\x1a\x65xternal_storage_available\x18= \x01(\x05\x12\x1e\n\x16internal_storage_total\x18> \x01(\x05\x12\"\n\x1ainternal_storage_available\x18? \x01(\x05\x12#\n\x1bgame_disk_storage_available\x18@ \x01(\x05\x12\x1f\n\x17game_disk_storage_total\x18\x41 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_avail_storage\x18\x42 \x01(\x05\x12%\n\x1d\x65xternal_sdcard_total_storage\x18\x43 \x01(\x05\x12\x10\n\x08login_by\x18I \x01(\x05\x12\x14\n\x0clibrary_path\x18J \x01(\t\x12\x12\n\nreg_avatar\x18L \x01(\x05\x12\x15\n\rlibrary_token\x18M \x01(\t\x12\x14\n\x0c\x63hannel_type\x18N \x01(\x05\x12\x10\n\x08\x63pu_type\x18O \x01(\x05\x12\x18\n\x10\x63pu_architecture\x18Q \x01(\t\x12\x1b\n\x13\x63lient_version_code\x18S \x01(\t\x12\x14\n\x0cgraphics_api\x18V \x01(\t\x12\x1d\n\x15supported_astc_bitset\x18W \x01(\r\x12\x1a\n\x12login_open_id_type\x18X \x01(\x05\x12\x18\n\x10\x61nalytics_detail\x18Y \x01(\x0c\x12\x14\n\x0cloading_time\x18\\ \x01(\r\x12\x17\n\x0frelease_channel\x18] \x01(\t\x12\x12\n\nextra_info\x18^ \x01(\t\x12 \n\x18\x61ndroid_engine_init_flag\x18_ \x01(\r\x12\x0f\n\x07if_push\x18\x61 \x01(\x05\x12\x0e\n\x06is_vpn\x18\x62 \x01(\x05\x12\x1c\n\x14origin_platform_type\x18\x63 \x01(\t\x12\x1d\n\x15primary_platform_type\x18\x64 \x01(\t\"5\n\x0cGameSecurity\x12\x0f\n\x07version\x18\x06 \x01(\x05\x12\x14\n\x0chidden_value\x18\x08 \x01(\x04\x62\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_MAJORLOGIN, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_MAJORLOGIN, 'MajorLoginReq_pb2', _globals)

# ---------- MajorLoginRes_pb2 ----------
DESCRIPTOR_MAJORLOGINRES = _descriptor_pool.Default().AddSerializedFile(b'\n\x13MajorLoginRes.proto\"\x87\x05\n\rMajorLoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x03\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\x05\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0c \x01(\x03\x12\x32\n\tblacklist\x18\r \x01(\x0b\x32\x1f.MajorLoginRes.BlacklistInfoRes\x12\x31\n\nqueue_info\x18\x0f \x01(\x0b\x32\x1d.MajorLoginRes.LoginQueueInfo\x12\x0e\n\x06tp_url\x18\x10 \x01(\t\x12\x15\n\rapp_server_id\x18\x11 \x01(\x03\x12\x0f\n\x07\x61no_url\x18\x12 \x01(\t\x12\x0f\n\x07ip_city\x18\x13 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x14 \x01(\t\x12\x0b\n\x03kts\x18\x15 \x01(\x03\x12\n\n\x02\x61k\x18\x16 \x01(\x0c\x12\x0b\n\x03\x61iv\x18\x17 \x01(\x0c\x1aQ\n\x10\x42lacklistInfoRes\x12\x12\n\nban_reason\x18\x01 \x01(\x05\x12\x17\n\x0f\x65xpire_duration\x18\x02 \x01(\x03\x12\x10\n\x08\x62\x61n_time\x18\x03 \x01(\x03\x1a\x66\n\x0eLoginQueueInfo\x12\r\n\x05\x41llow\x18\x01 \x01(\x08\x12\x16\n\x0equeue_position\x18\x02 \x01(\x03\x12\x16\n\x0eneed_wait_secs\x18\x03 \x01(\x03\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08\x62\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR_MAJORLOGINRES, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR_MAJORLOGINRES, 'MajorLoginRes_pb2', _globals)

# Now we can import the generated classes as if they were from the original modules.
# We'll alias them for convenience.
import MajorLoginReq_pb2 as mLpB
import MajorLoginRes_pb2 as mLrPb

# ============================================================================
#  LOGGING
# ============================================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
#  DATABASE
# ============================================================================
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_admin INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            command TEXT,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            error TEXT,
            traceback TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'false')")
    conn.commit()
    conn.close()

def db_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    result = None
    if fetchone:
        result = c.fetchone()
    elif fetchall:
        result = c.fetchall()
    if commit:
        conn.commit()
    conn.close()
    return result

def get_user(user_id):
    return db_query("SELECT * FROM users WHERE user_id = ?", (user_id,), fetchone=True)

def register_user(user_id, username, first_name, last_name):
    if not get_user(user_id):
        db_query(
            "INSERT INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, last_name),
            commit=True
        )
        logger.info(f"Registered new user: {user_id} ({username})")
    else:
        db_query(
            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
            (user_id,),
            commit=True
        )

def log_command(user_id, command, response=""):
    db_query(
        "INSERT INTO logs (user_id, command, response) VALUES (?, ?, ?)",
        (user_id, command, response[:500]),
        commit=True
    )

def log_error(user_id, error, traceback=""):
    db_query(
        "INSERT INTO errors (user_id, error, traceback) VALUES (?, ?, ?)",
        (user_id, str(error)[:500], traceback[:1000]),
        commit=True
    )

def is_maintenance():
    val = db_query("SELECT value FROM settings WHERE key = 'maintenance'", fetchone=True)
    return val and val[0].lower() == 'true'

def set_maintenance(mode: bool):
    db_query("UPDATE settings SET value = ? WHERE key = 'maintenance'", ('true' if mode else 'false',), commit=True)

# ============================================================================
#  RATE LIMITING
# ============================================================================
user_last_command = {}

def rate_limit(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        now = time.time()
        last = user_last_command.get(user_id, 0)
        if now - last < 1:  # 1 second cooldown
            await update.message.reply_text("⏳ Please wait a moment before sending another command.")
            return
        user_last_command[user_id] = now
        return await func(update, context, *args, **kwargs)
    return wrapper

# ============================================================================
#  ORIGINAL HELPER FUNCTIONS (from app.py)
# ============================================================================
small = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
}

def smallcaps(text: str) -> str:
    return ''.join(small.get(ch, ch) for ch in text)

def label_value(label: str, value: str) -> str:
    return f"{smallcaps(label)}: {smallcaps(str(value))}"

def convert_seconds(s):
    d, h = divmod(s, 86400)
    h, m = divmod(h, 3600)
    m, s = divmod(m, 60)
    return f"{d} Day {h} Hour {m} Min {s} Sec"

def format_response_text(response_text, title="API Response"):
    try:
        parsed = json.loads(response_text)
        result_code = parsed.get("result")
        if result_code == 0:
            return f"✅ {smallcaps(title)}: {smallcaps('SUCCESS')}"
        elif result_code is not None:
            error_msg = parsed.get("error", "Unknown error")
            return f"❌ {smallcaps(title)}: {smallcaps('FAILED')} ({smallcaps('Code')} {result_code} | {error_msg})"
        else:
            return f"ℹ️ {smallcaps(title)}: {smallcaps('Completed (No standard result code)')}"
    except Exception:
        if '"result": 0' in response_text.replace(" ", ""):
            return f"✅ {smallcaps(title)}: {smallcaps('SUCCESS')}"
        else:
            return f"❌ {smallcaps(title)}: {smallcaps('Unrecognized response format')}"

def get_player_info(access_token):
    try:
        player_url = f"https://api-otrss.garena.com/support/callback/?access_token={access_token}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(player_url, headers=headers, timeout=15, allow_redirects=True)
        parsed = urllib.parse.urlparse(resp.url)
        params = urllib.parse.parse_qs(parsed.query)
        uid = params.get("account_id", ["Unknown"])[0]
        nickname = params.get("nickname", ["Unknown"])[0]
        region = params.get("region", ["Unknown"])[0]
        return {"uid": uid, "nickname": urllib.parse.unquote(nickname), "region": region}
    except Exception:
        return {"uid": "Unknown", "nickname": "Unknown", "region": "Unknown"}

def check_bind_info(access_token):
    lines = []
    info = get_player_info(access_token)
    lines.append(smallcaps("👤 Player Information"))
    lines.append(label_value("UID", info['uid']))
    lines.append(label_value("Nickname", info['nickname']))
    lines.append(label_value("Region", info['region']))
    lines.append("")

    url = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
    payload = {'app_id': "100067", 'access_token': access_token}
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }
    try:
        response = requests.get(url, params=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            email = data.get("email", "")
            email_to_be = data.get("email_to_be", "")
            countdown = data.get("request_exec_countdown", 0)
            countdown_human = convert_seconds(countdown)
            result_code = data.get("result", -1)

            lines.append(smallcaps("🔐 Bind Information"))
            lines.append(label_value("Current Email", email if email else 'None'))
            lines.append(label_value("Pending Email", email_to_be if email_to_be else 'None'))
            if email_to_be:
                lines.append(label_value("Countdown", countdown_human))
            if result_code == 0:
                lines.append(label_value("Result", "✅ SUCCESS"))
            else:
                lines.append(label_value("Result", f"❌ FAILED (Code: {result_code})"))

            if email == "" and email_to_be != "":
                lines.append(f"ℹ️ {smallcaps('Summary')}: {smallcaps(f'Pending confirmation for {email_to_be} – confirms in {countdown_human}')}")
            elif email != "" and email_to_be == "":
                lines.append(f"ℹ️ {smallcaps('Summary')}: {smallcaps(f'Email confirmed: {email}')}")
            elif email == "" and email_to_be == "":
                lines.append(f"ℹ️ {smallcaps('Summary')}: {smallcaps('No recovery email set')}")
        else:
            lines.append(f"❌ {smallcaps('API Error')} (Status {response.status_code})")
    except Exception as e:
        lines.append(f"❌ {smallcaps('Failed to fetch info')}: {smallcaps(str(e))}")
    return "\n".join(lines)

def bind_email_flow(access_token, email, otp, security_code):
    headers = {
        "User-Agent": "GarenaMSDK/4.0.30",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    send_otp_url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
    send_otp_data = {
        "email": email,
        "locale": "en_PK",
        "region": "PK",
        "app_id": "100067",
        "access_token": access_token
    }
    resp_send = requests.post(send_otp_url, headers=headers, data=send_otp_data)
    send_msg = format_response_text(resp_send.text, "Send OTP")
    if '"result":0' not in resp_send.text.replace(" ", ""):
        return False, f"❌ {smallcaps('Send OTP failed')}.\n{send_msg}"

    verify_url = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
    verify_data = {
        "app_id": "100067",
        "access_token": access_token,
        "email": email,
        "code": otp,
        "otp": otp,
        "type": "1"
    }
    resp_verify = requests.post(verify_url, headers=headers, data=verify_data)
    verify_msg = format_response_text(resp_verify.text, "Verify OTP")
    try:
        verifier_token = resp_verify.json().get("verifier_token", "")
    except:
        verifier_token = ""
    if not verifier_token:
        return False, f"❌ {smallcaps('Verification failed')} – {smallcaps('no verifier token')}.\n{verify_msg}"

    bind_url = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
    bind_data = {
        "email": email,
        "app_id": "100067",
        "access_token": access_token,
        "verifier_token": verifier_token,
        "secondary_password": security_code
    }
    resp_bind = requests.post(bind_url, headers=headers, data=bind_data)
    bind_msg = format_response_text(resp_bind.text, "Final Bind Request")
    return True, f"✅ {smallcaps('Bind process completed')}.\n{send_msg}\n{verify_msg}\n{bind_msg}"

def unbind_email_flow(access_token, method, otp_or_code):
    headers = {
        "User-Agent": "GarenaMSDK/4.0.30",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    try:
        url_info = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
        info_payload = {'app_id': "100067", 'access_token': access_token}
        r_info = requests.get(url_info, params=info_payload, headers=headers, timeout=10)
        email = r_info.json().get("email", "")
    except:
        email = ""
    if not email:
        return False, f"❌ {smallcaps('No currently Bɪɴᴅ email found')}. {smallcaps('Cannot unbind.')}"

    identity_token = None
    if method == 1:  # OTP
        send_otp_url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
        send_data = {"email": email, "locale": "en_PK", "region": "PK",
                     "app_id": "100067", "access_token": access_token}
        resp = requests.post(send_otp_url, headers=headers, data=send_data)
        send_msg = format_response_text(resp.text, "Send OTP")
        if '"result":0' not in resp.text.replace(" ", ""):
            return False, f"❌ {smallcaps('Send OTP failed')}.\n{send_msg}"

        verify_url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
        verify_data = {"email": email, "app_id": "100067", "access_token": access_token, "otp": otp_or_code}
        resp = requests.post(verify_url, headers=headers, data=verify_data)
        verify_msg = format_response_text(resp.text, "Verify Identity")
        try:
            identity_token = resp.json().get("identity_token")
        except:
            identity_token = None
        if not identity_token:
            return False, f"❌ {smallcaps('Identity verification failed')}.\n{verify_msg}"
    else:  # Security Code
        hashed_code = hashlib.sha256(otp_or_code.encode('utf-8')).hexdigest()
        verify_url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
        verify_data = {"email": email, "app_id": "100067", "access_token": access_token,
                       "secondary_password": hashed_code}
        resp = requests.post(verify_url, headers=headers, data=verify_data)
        verify_msg = format_response_text(resp.text, "Verify Identity")
        try:
            identity_token = resp.json().get("identity_token")
        except:
            identity_token = None
        if not identity_token:
            return False, f"❌ {smallcaps('Identity verification failed')}.\n{verify_msg}"

    unbind_url = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
    unbind_data = {"app_id": "100067", "access_token": access_token, "identity_token": identity_token}
    resp = requests.post(unbind_url, headers=headers, data=unbind_data)
    unbind_msg = format_response_text(resp.text, "Unbind Request")
    return True, f"✅ {smallcaps('Unbind completed')}.\n{verify_msg}\n{unbind_msg}"

def change_bind_flow(access_token, method, old_code, new_email, new_otp):
    headers = {
        "User-Agent": "GarenaMSDK/4.0.30",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    try:
        url_info = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
        info_payload = {'app_id': "100067", 'access_token': access_token}
        r_info = requests.get(url_info, params=info_payload, headers=headers, timeout=10)
        old_email = r_info.json().get("email", "")
    except:
        old_email = ""
    if not old_email:
        return False, f"❌ {smallcaps('No currently Bɪɴᴅ email found')}."

    identity_token = None
    if method == 1:  # OTP
        send_otp_url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
        send_data = {"email": old_email, "locale": "en_PK", "region": "PK",
                     "app_id": "100067", "access_token": access_token}
        resp = requests.post(send_otp_url, headers=headers, data=send_data)
        send_msg = format_response_text(resp.text, "Send OTP (old)")
        if '"result":0' not in resp.text.replace(" ", ""):
            return False, f"❌ {smallcaps('Send OTP to old email failed')}.\n{send_msg}"

        verify_url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
        verify_data = {"email": old_email, "app_id": "100067", "access_token": access_token, "otp": old_code}
        resp = requests.post(verify_url, headers=headers, data=verify_data)
        verify_msg = format_response_text(resp.text, "Verify Identity")
        try:
            identity_token = resp.json().get("identity_token")
        except:
            identity_token = None
        if not identity_token:
            return False, f"❌ {smallcaps('Identity verification failed')}.\n{verify_msg}"
    else:  # Security Code
        hashed_code = hashlib.sha256(old_code.encode('utf-8')).hexdigest()
        verify_url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
        verify_data = {"email": old_email, "app_id": "100067", "access_token": access_token,
                       "secondary_password": hashed_code}
        resp = requests.post(verify_url, headers=headers, data=verify_data)
        verify_msg = format_response_text(resp.text, "Verify Identity")
        try:
            identity_token = resp.json().get("identity_token")
        except:
            identity_token = None
        if not identity_token:
            return False, f"❌ {smallcaps('Identity verification failed')}.\n{verify_msg}"

    send_otp_url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
    send_data = {"email": new_email, "locale": "en_PK", "region": "PK",
                 "app_id": "100067", "access_token": access_token}
    resp = requests.post(send_otp_url, headers=headers, data=send_data)
    send_new_msg = format_response_text(resp.text, "Send OTP (new)")
    if '"result":0' not in resp.text.replace(" ", ""):
        return False, f"❌ {smallcaps('Send OTP to new email failed')}.\n{send_new_msg}"

    verify_otp_url = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
    verify_otp_data = {"email": new_email, "app_id": "100067", "access_token": access_token, "otp": new_otp}
    resp = requests.post(verify_otp_url, headers=headers, data=verify_otp_data)
    verify_otp_msg = format_response_text(resp.text, "Verify OTP (new)")
    try:
        verifier_token = resp.json().get("verifier_token")
    except:
        verifier_token = None
    if not verifier_token:
        return False, f"❌ {smallcaps('New email OTP verification failed')}.\n{verify_otp_msg}"

    rebind_url = "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request"
    rebind_data = {"identity_token": identity_token, "email": new_email,
                   "app_id": "100067", "verifier_token": verifier_token,
                   "access_token": access_token}
    resp = requests.post(rebind_url, headers=headers, data=rebind_data)
    rebind_msg = format_response_text(resp.text, "Rebind Request")
    return True, f"✅ {smallcaps('Change bind completed')}.\n{verify_msg}\n{send_new_msg}\n{verify_otp_msg}\n{rebind_msg}"

def cancel_bind_request(access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.30",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {"app_id": "100067", "access_token": access_token}
    response = requests.post(url, headers=headers, data=data)
    return format_response_text(response.text, "Cancel Request")

def eat_to_access_token(eat_input):
    eat_token = None
    if "http" in eat_input or "?" in eat_input:
        parsed_url = urllib.parse.urlparse(eat_input)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'eat' in query_params:
            eat_token = query_params['eat'][0]
    else:
        eat_token = eat_input.strip()
    if not eat_token:
        return False, f"❌ {smallcaps('Could not find an EAT token')} in your input.", None

    api_url = f"https://api-otrss.garena.com/support/callback/?access_token={eat_token}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36"
    }
    try:
        response = requests.get(api_url, headers=headers, allow_redirects=True, timeout=15)
        parsed = urllib.parse.urlparse(response.url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'access_token' in params:
            access_token = params['access_token'][0]
            account_id = params.get('account_id', ['Unknown'])[0]
            nickname = urllib.parse.unquote(params.get('nickname', ['Unknown'])[0])
            region = params.get('region', ['Unknown'])[0]
            msg = (
                f"✅ {smallcaps('Conversion successful')}!\n"
                f"{label_value('Nickname', nickname)}\n"
                f"{label_value('Account ID', account_id)}\n"
                f"{label_value('Region', region)}\n"
                f"{smallcaps('Access Token')}:\n{access_token}"
            )
            return True, msg, access_token
        else:
            return False, f"❌ {smallcaps('Access token not found')}. {smallcaps('Token might be expired or invalid.')}", None
    except Exception as e:
        return False, f"❌ {smallcaps('Error')}: {smallcaps(str(e))}", None

def revoke_access_token(access_token):
    api_url = f"https://api-otrss.garena.com/support/callback/?access_token={access_token}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    nickname = "Unknown"
    account_id = "Unknown"
    region = "Unknown"
    is_valid = False
    try:
        res = requests.get(api_url, headers=headers, allow_redirects=True, timeout=15)
        parsed = urllib.parse.urlparse(res.url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'access_token' in params:
            is_valid = True
            nickname = urllib.parse.unquote(params.get('nickname', ['Unknown'])[0])
            account_id = params.get('account_id', ['Unknown'])[0]
            region = params.get('region', ['Unknown'])[0]
    except:
        pass
    if not is_valid:
        return f"❌ {smallcaps('Token is already invalid, expired, or revoked')}!"

    refresh_token = "1380dcb63ab3a077dc05bdf0b25ba4497c403a5b4eae96d7203010eafa6c83a8"
    logout_url = f"https://100067.connect.garena.com/oauth/logout?access_token={access_token}&refresh_token={refresh_token}"
    try:
        logout_res = requests.get(logout_url, headers=headers, timeout=15)
        if logout_res.status_code == 200 and "error" not in logout_res.text:
            return (
                f"✅ {smallcaps('Token revoked successfully')}!\n"
                f"{label_value('Nickname', nickname)}\n"
                f"{label_value('Account ID', account_id)}\n"
                f"{label_value('Region', region)}\n"
                f"{smallcaps('Status')}: {smallcaps('Logged out & revoked')}"
            )
        else:
            return f"❌ {smallcaps('Failed to revoke token')}! {smallcaps('Server responded with an error.')}"
    except Exception as e:
        return f"❌ {smallcaps('Error')}: {smallcaps(str(e))}"

# ------------- Protobuf / Login History functions -------------
AeSkEy = b'Yg&tc%DEuh6%Zc^8'
AeSiV  = b'6oyZDr22E3ychjM%'

PLATFORM_MAP = {
    3: "Facebook", 4: "Guest", 5: "VK",
    6: "Huawei", 8: "Google", 11: "X (Twitter)", 13: "AppleId",
}

def enc(d):
    return AES.new(AeSkEy, AES.MODE_CBC, AeSiV).encrypt(pad(d, 16))

def dec(d):
    return unpad(AES.new(AeSkEy, AES.MODE_CBC, AeSiV).decrypt(d), 16)

def build_majorlogin(tok, open_id, p_type):
    m = mLpB.MajorLogin()
    m.event_time = str(datetime.now())[:-7]
    m.game_name = "free fire"
    m.platform_id = p_type
    m.client_version = "1.120.1"
    m.system_software = "Android OS 9 / API-28"
    m.system_hardware = "Handheld"
    m.telecom_operator = "Verizon"
    m.network_type = "WIFI"
    m.screen_width = 1920
    m.screen_height = 1080
    m.screen_dpi = "280"
    m.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    m.memory = 3003
    m.gpu_renderer = "Adreno (TM) 640"
    m.gpu_version = "OpenGL ES 3.1 v1.46"
    m.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    m.client_ip = "223.191.51.89"
    m.language = "en"
    m.open_id = open_id
    m.open_id_type = str(p_type)
    m.device_type = "Handheld"
    m.access_token = tok
    m.platform_sdk_id = 1
    m.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    m.login_by = 3
    m.channel_type = 3
    m.cpu_type = 2
    m.cpu_architecture = "64"
    m.client_version_code = "2019118695"
    m.login_open_id_type = p_type
    m.origin_platform_type = str(p_type)
    m.primary_platform_type = str(p_type)
    return enc(m.SerializeToString())

def read_varint(data, offset):
    res = 0; shift = 0
    while True:
        if offset >= len(data):
            break
        b = data[offset]; offset += 1
        res |= (b & 0x7f) << shift
        if not (b & 0x80):
            break
        shift += 7
    return res, offset

def parse_record(data):
    rec = {}; offset = 0
    while offset < len(data):
        tag, offset = read_varint(data, offset)
        wt, f = tag & 7, tag >> 3
        if wt == 0:
            val, offset = read_varint(data, offset)
            if f == 1:
                rec['ts'] = val
            elif f == 2:
                rec['ram'] = val
        elif wt == 2:
            length, offset = read_varint(data, offset)
            val = data[offset:offset+length]; offset += length
            if f == 3:
                rec['dev'] = val.decode(errors='ignore')
            elif f == 4:
                rec['arch'] = val.decode(errors='ignore')
        else:
            break
    return rec

def parse_history_protobuf(data):
    records = []; offset = 0
    while offset < len(data):
        tag, offset = read_varint(data, offset)
        wt, f = tag & 7, tag >> 3
        if wt == 0:
            val, offset = read_varint(data, offset)
        elif wt == 2:
            length, offset = read_varint(data, offset)
            val = data[offset:offset+length]; offset += length
            if f == 1:
                records.append(parse_record(val))
        else:
            break
    return records

def get_login_history(token):
    jwt_token = None
    if token.startswith("ey") and "." in token:
        jwt_token = token
    else:
        open_id = None
        try:
            r = requests.get(f"https://100067.connect.garena.com/oauth/token/inspect?token={token}",
                             headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
            open_id = r.get("open_id")
        except:
            pass
        if not open_id:
            try:
                uid_headers = {"access-token": token, "user-agent": "Mozilla/5.0"}
                uid_res = requests.get("https://prod-api.reward.ff.garena.com/redemption/api/auth/inspect_token/",
                                       headers=uid_headers, verify=False, timeout=5).json()
                uid = uid_res.get("uid")
                if uid:
                    openid_res = requests.post("https://topup.pk/api/auth/player_id_login",
                                               json={"app_id": 100067, "login_id": str(uid)},
                                               verify=False, timeout=5).json()
                    open_id = openid_res.get("open_id")
            except:
                pass
        if not open_id:
            return f"❌ {smallcaps('Failed to extract Open ID')}. {smallcaps('Token is likely invalid or expired.')}"

        platforms = [8, 3, 4, 6]
        for p_type in platforms:
            pl = build_majorlogin(token, open_id, p_type)
            try:
                headers = {
                    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-S908E Build/TP1A.220624.014)",
                    "Connection": "Keep-Alive",
                    "Accept-Encoding": "gzip",
                    "Content-Type": "application/octet-stream",
                    "Expect": "100-continue",
                    "X-GA": "v1 1",
                    "X-Unity-Version": "2018.4.11f1",
                    "ReleaseVersion": "OB54"
                }
                x = requests.post("https://loginbp.ggpolarbear.com/MajorLogin", headers=headers,
                                  data=pl, timeout=10, verify=False)
                if x.status_code == 200:
                    res = mLrPb.MajorLoginRes()
                    try:
                        res.ParseFromString(dec(x.content))
                    except:
                        res.ParseFromString(x.content)
                    if res.token:
                        jwt_token = res.token
                        break
            except:
                continue
        if not jwt_token:
            return f"❌ {smallcaps('MajorLogin failed')} across all platforms. {smallcaps('Token might be blocked.')}"

    try:
        payload_b64 = jwt_token.split('.')[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
        name = urllib.parse.unquote(decoded.get("nickname", "Unknown"))
        uid = decoded.get("account_id", "Unknown")
        region = decoded.get("lock_region", "Unknown")
        p_id = decoded.get("external_type", 0)
        platform = PLATFORM_MAP.get(p_id, f"Unknown ({p_id})")
        info_lines = [
            smallcaps("👤 Player Info"),
            label_value("Account Name", name),
            label_value("Account ID", uid),
            label_value("Platform", platform),
            label_value("Region", region)
        ]
    except:
        info_lines = []

    hH = {
        "Expect": "100-continue",
        "Authorization": f"Bearer {jwt_token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB54",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        "Host": "client.ind.freefiremobile.com",
        "Connection": "close"
    }
    try:
        r = requests.post("https://client.ind.freefiremobile.com/GetLoginHistory",
                          headers=hH, data=enc(b""), timeout=15, verify=False)
        if r.status_code != 200:
            return f"❌ {smallcaps('History Request Failed')}: HTTP {r.status_code}"
        try:
            d = dec(r.content)
        except:
            d = r.content
        records = parse_history_protobuf(d)
        history_lines = [smallcaps("📜 Login History")]
        if not records:
            history_lines.append(smallcaps("No login history records found."))
        else:
            for i, rec in enumerate(records, 1):
                ts_raw = rec.get('ts', 0)
                try:
                    date_str = datetime.fromtimestamp(ts_raw).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date_str = "Invalid Format"
                dev = rec.get('dev', 'Unknown Device')
                arch = rec.get('arch', 'Unknown Architecture')
                ram = rec.get('ram', 0)
                history_lines.append(
                    f"{smallcaps(f'Record #{i}')}\n"
                    f"{label_value('Timestamp', ts_raw)}\n"
                    f"{label_value('Last Login', date_str)}\n"
                    f"{label_value('Device', dev)}\n"
                    f"{label_value('Architecture', arch)}\n"
                    f"{label_value('RAM', f'{ram} MB')}"
                )
        return "\n".join(info_lines + [""] + history_lines)
    except Exception as e:
        return f"❌ {smallcaps('Error fetching history')}: {smallcaps(str(e))}"

def check_Bɪɴᴅ_accounts(access_token):
    url = "https://100067.connect.garena.com/bind/app/platform/info/get"
    params = {"access_token": access_token}
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"❌ {smallcaps('Failed to fetch data')} (HTTP {response.status_code})"
        d = response.json()
        Bɪɴᴅed = d.get("Bɪɴᴅed_accounts", [])
        available = d.get("available_platforms", [])
        PLATFORM_MAP = {
            1: "Garena", 3: "Facebook", 4: "Guest", 5: "VK",
            6: "Huawei", 7: "Apple", 8: "Google", 10: "GameCenter / Line",
            11: "X (Twitter)", 13: "Apple ID", 28: "Line", 35: "TikTok"
        }
        lines = [smallcaps("🔗 Platform Bind Information")]
        lines.append(smallcaps("Bɪɴᴅ Accounts:"))
        if not Bɪɴᴅed:
            lines.append(smallcaps("• No third‑party platforms are currently Bɪɴᴅ."))
        else:
            for p_id in Bɪɴᴅed:
                p_name = PLATFORM_MAP.get(p_id, f"Unknown ({p_id})")
                lines.append(f"• {smallcaps(p_name)}")
        lines.append("")
        lines.append(smallcaps("Available Platforms:"))
        if not available:
            lines.append(smallcaps("• None"))
        else:
            for p_id in available:
                p_name = PLATFORM_MAP.get(p_id, f"Unknown ({p_id})")
                lines.append(f"• {smallcaps(p_name)}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ {smallcaps('Error')}: {smallcaps(str(e))}"

def send_unsubscribe_otp(email: str) -> str:
    url = f"https://allo-gang.vercel.app/api/send-code?email={email}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return (
                "❌ Oᴛᴘ Sᴇɴᴅ Fᴀɪʟᴇᴅ\n\n"
                "📩 Wᴇ Cᴏᴜʟᴅ Nᴏᴛ Sᴇɴᴅ Tʜᴇ Sɪɴɢʟᴇ Uɴsᴜʙsᴄʀɪʙᴇ Oᴛᴘ.\n\n"
                "⚠️ Pʟᴇᴀsᴇ Cʜᴇᴄᴋ Yᴏᴜʀ Eᴍᴀɪʟ Aᴅᴅʀᴇss Aɴᴅ Tʀʏ Aɢᴀɪɴ Lᴀᴛᴇʀ."
            )
        data = response.json()
        status = data.get("status")
        garena = data.get("garena_response", {})
        result = garena.get("result")
        if status == "success" and result == 0:
            return (
                f"✅ Sɪɴɢʟᴇ Uɴsᴜʙsᴄʀɪʙᴇ Oᴛᴘ Sᴇɴᴛ Sᴜᴄᴄᴇssғᴜʟʟʏ!\n\n"
                f"📧 Eᴍᴀɪʟ: {email}\n\n"
                f"📩 Sᴛᴀᴛᴜs: Oᴛᴘ Hᴀs Bᴇᴇɴ Sᴇɴᴛ Tᴏ Yᴏᴜʀ Eᴍᴀɪʟ."
            )
        else:
            return (
                "❌ Oᴛᴘ Sᴇɴᴅ Fᴀɪʟᴇᴅ\n\n"
                "📩 Wᴇ Cᴏᴜʟᴅ Nᴏᴛ Sᴇɴᴅ Tʜᴇ Sɪɴɢʟᴇ Uɴsᴜʙsᴄʀɪʙᴇ Oᴛᴘ.\n\n"
                "⚠️ Pʟᴇᴀsᴇ Cʜᴇᴄᴋ Yᴏᴜʀ Eᴍᴀɪʟ Aᴅᴅʀᴇss Aɴᴅ Tʀʏ Aɢᴀɪɴ Lᴀᴛᴇʀ."
            )
    except:
        return (
            "❌ Oᴛᴘ Sᴇɴᴅ Fᴀɪʟᴇᴅ\n\n"
            "📩 Wᴇ Cᴏᴜʟᴅ Nᴏᴛ Sᴇɴᴅ Tʜᴇ Sɪɴɢʟᴇ Uɴsᴜʙsᴄʀɪʙᴇ Oᴛᴘ.\n\n"
            "⚠️ Pʟᴇᴀsᴇ Cʜᴇᴄᴋ Yᴏᴜʀ Eᴍᴀɪʟ Aᴅᴅʀᴇss Aɴᴅ Tʀʏ Aɢᴀɪɴ Lᴀᴛᴇʀ."
        )

# ============================================================================
#  TELEGRAM BOT HANDLERS
# ============================================================================
# Conversation states
(TOKEN_INPUT, EMAIL_INPUT, OTP_INPUT, SECURITY_INPUT,
 CHANGE_METHOD, OLD_CODE, NEW_EMAIL, NEW_OTP,
 UNBIND_METHOD, UNBIND_CODE,
 EAT_INPUT, UNSUBSCRIBE_EMAIL) = range(12)

# Command list for keyboard
COMMANDS = [
    {"text": "🔍 Cʜᴇᴄᴋ Bɪɴᴅ Iɴꜰᴏ", "style": "primary"},
    {"text": "📧 Bɪɴᴅ Eᴍᴀɪʟ", "style": "success"},
    {"text": "🔓 Uɴʙɪɴᴅ Eᴍᴀɪʟ", "style": "danger"},
    {"text": "🔄 Cʜᴀɴɢᴇ Bɪɴᴅ Eᴍᴀɪʟ", "style": "primary"},
    {"text": "❌ Cᴀɴᴄᴇʟ Bɪɴᴅ Rᴇǫᴜᴇsᴛ", "style": "danger"},
    {"text": "🔄 Eᴀᴛ Tᴏ Aᴄᴄᴇss Tᴏᴋᴇɴ", "style": "success"},
    {"text": "🚫 Rᴇᴠᴏᴋᴇ Aᴄᴄᴇss Tᴏᴋᴇɴ", "style": "danger"},
    {"text": "📜 Gᴇᴛ Lᴏɢɪɴ Hɪsᴛᴏʀʏ", "style": "primary"},
    {"text": "🔗 Cʜᴇᴄᴋ Bɪɴᴅ Aᴄᴄᴏᴜɴᴛs", "style": "primary"},
    {"text": "👤 Oᴡɴᴇʀ Dᴇᴛᴀɪʟs", "style": "success"},
    {"text": "📩 Sᴇɴᴅ Sɪɴɢʟᴇ Uɴsᴜʙsᴄʀɪʙᴇ Oᴛᴘ", "style": "primary"},
]
COMMAND_TEXTS = [cmd["text"] for cmd in COMMANDS]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username, user.first_name, user.last_name)
    if is_maintenance() and user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ Bot is under maintenance. Please try again later.")
        return
    keyboard = []
    for i in range(0, len(COMMANDS), 2):
        row = []
        row.append(KeyboardButton(COMMANDS[i]["text"]))
        if i+1 < len(COMMANDS):
            row.append(KeyboardButton(COMMANDS[i+1]["text"]))
        keyboard.append(row)
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        smallcaps("🤖 Garena Bind Tool Bot\nChoose an option:"),
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def handle_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_maintenance() and user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ Bot is under maintenance. Please try again later.")
        return ConversationHandler.END
    text = update.message.text
    if text not in COMMAND_TEXTS:
        await update.message.reply_text(smallcaps("Unknown command. Please use the buttons below."))
        return ConversationHandler.END

    if text == "🔍 Cʜᴇᴄᴋ Bɪɴᴅ Iɴꜰᴏ":
        await update.message.reply_text(smallcaps("Please send your Access Token:"))
        context.user_data['next_action'] = 'bind_info'
        return TOKEN_INPUT
    elif text == "📧 Bɪɴᴅ Eᴍᴀɪʟ":
        await update.message.reply_text(smallcaps("Please send your Access Token:"))
        context.user_data['next_action'] = 'bind_email'
        return TOKEN_INPUT
    elif text == "🔓 Uɴʙɪɴᴅ Eᴍᴀɪʟ":
        keyboard = [
            [InlineKeyboardButton(smallcaps("🔑 OTP"), callback_data="unbind_otp")],
            [InlineKeyboardButton(smallcaps("🔐 Security Code"), callback_data="unbind_sec")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            smallcaps("Choose unbind method:"),
            reply_markup=reply_markup
        )
        return UNBIND_METHOD
    elif text == "🔄 Cʜᴀɴɢᴇ Bɪɴᴅ Eᴍᴀɪʟ":
        keyboard = [
            [InlineKeyboardButton(smallcaps("🔑 OTP"), callback_data="change_otp")],
            [InlineKeyboardButton(smallcaps("🔐 Security Code"), callback_data="change_sec")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            smallcaps("Choose change method:"),
            reply_markup=reply_markup
        )
        return CHANGE_METHOD
    elif text == "❌ Cᴀɴᴄᴇʟ Bɪɴᴅ Rᴇǫᴜᴇsᴛ":
        await update.message.reply_text(smallcaps("Send your Access Token to cancel pending bind request:"))
        context.user_data['next_action'] = 'cancel_bind'
        return TOKEN_INPUT
    elif text == "🔄 Eᴀᴛ Tᴏ Aᴄᴄᴇss Tᴏᴋᴇɴ":
        await update.message.reply_text(smallcaps("Send the EAT token (or full EAT URL):"))
        context.user_data['next_action'] = 'eat_to_token'
        return EAT_INPUT
    elif text == "🚫 Rᴇᴠᴏᴋᴇ Aᴄᴄᴇss Tᴏᴋᴇɴ":
        await update.message.reply_text(smallcaps("Send the Access Token you wish to revoke:"))
        context.user_data['next_action'] = 'revoke_token'
        return TOKEN_INPUT
    elif text == "📜 Gᴇᴛ Lᴏɢɪɴ Hɪsᴛᴏʀʏ":
        await update.message.reply_text(smallcaps("Send your Access Token (or Game JWT token):"))
        context.user_data['next_action'] = 'login_history'
        return TOKEN_INPUT
    elif text == "🔗 Cʜᴇᴄᴋ Bɪɴᴅ Aᴄᴄᴏᴜɴᴛs":
        await update.message.reply_text(smallcaps("Send your Access Token:"))
        context.user_data['next_action'] = 'Bɪɴᴅ_accounts'
        return TOKEN_INPUT
    elif text == "👤 Oᴡɴᴇʀ Dᴇᴛᴀɪʟs":
        owner_text = (
            "👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀ\n"
            "\n"
            "├─ 🕷️ Nᴀᴍᴇ : Dɢ Dʀɪғᴛ\n"
            "├─ 📩 Tᴇʟᴇɢʀᴀᴍ : @DG_DRIFT\n"
            "├─ 📢 Cʜᴀɴɴᴇʟ : @DGDRIFT\n"
            "├─ 🛡️ Vᴇʀsɪᴏɴ : v2.0 • Pʀᴇᴍɪᴜᴍ Eᴅɪᴛɪᴏɴ\n"
            "└─ 💬 Sᴜᴘᴘᴏʀᴛ : @DGDRIFT"
        )
        await update.message.reply_text(owner_text)
        return ConversationHandler.END
    elif text == "📩 Sᴇɴᴅ Sɪɴɢʟᴇ Uɴsᴜʙsᴄʀɪʙᴇ Oᴛᴘ":
        await update.message.reply_text(smallcaps("Please send the Gmail address to send the unsubscribe OTP:"))
        return UNSUBSCRIBE_EMAIL
    else:
        await update.message.reply_text(smallcaps("Unknown command."))
        return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "unbind_otp":
        context.user_data['unbind_method'] = 1
        await query.edit_message_text(smallcaps("Send your Access Token:"))
        context.user_data['next_action'] = 'unbind_email'
        return TOKEN_INPUT
    elif data == "unbind_sec":
        context.user_data['unbind_method'] = 2
        await query.edit_message_text(smallcaps("Send your Access Token:"))
        context.user_data['next_action'] = 'unbind_email'
        return TOKEN_INPUT
    elif data == "change_otp":
        context.user_data['change_method'] = 1
        await query.edit_message_text(smallcaps("Send your Access Token:"))
        context.user_data['next_action'] = 'change_bind'
        return TOKEN_INPUT
    elif data == "change_sec":
        context.user_data['change_method'] = 2
        await query.edit_message_text(smallcaps("Send your Access Token:"))
        context.user_data['next_action'] = 'change_bind'
        return TOKEN_INPUT
    else:
        await query.edit_message_text(smallcaps("Unknown option."))
        return ConversationHandler.END

async def token_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    if not token:
        await update.message.reply_text(smallcaps("❌ Token cannot be empty. Please try again or /cancel."))
        return TOKEN_INPUT

    action = context.user_data.get('next_action')
    processing_msg = await update.message.reply_text(smallcaps("⏳ Pʀᴏᴄᴇssɪɴɢ..."))

    if action == 'bind_info':
        result = check_bind_info(token)
    elif action == 'cancel_bind':
        result = cancel_bind_request(token)
    elif action == 'revoke_token':
        result = revoke_access_token(token)
    elif action == 'login_history':
        result = get_login_history(token)
    elif action == 'Bɪɴᴅ_accounts':
        result = check_Bɪɴᴅ_accounts(token)
    elif action == 'bind_email':
        context.user_data['access_token'] = token
        await processing_msg.edit_text(smallcaps("Now send the email address you want to bind:"))
        return EMAIL_INPUT
    elif action == 'unbind_email':
        context.user_data['access_token'] = token
        method = context.user_data.get('unbind_method')
        if method == 1:
            await processing_msg.edit_text(smallcaps("Send the OTP received on your current email:"))
            return UNBIND_CODE
        else:
            await processing_msg.edit_text(smallcaps("Send your 6‑digit Security Code:"))
            return UNBIND_CODE
    elif action == 'change_bind':
        context.user_data['access_token'] = token
        method = context.user_data.get('change_method')
        if method == 1:
            await processing_msg.edit_text(smallcaps("Send the OTP received on your current email:"))
            return OLD_CODE
        else:
            await processing_msg.edit_text(smallcaps("Send your 6‑digit Security Code:"))
            return OLD_CODE
    elif action == 'eat_to_token':
        await processing_msg.edit_text(smallcaps("Please use the EAT option from the main menu."))
        return ConversationHandler.END
    else:
        await processing_msg.edit_text(smallcaps("Unexpected action. Please start over with /start."))
        return ConversationHandler.END

    await processing_msg.edit_text(result)
    return ConversationHandler.END

async def email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if not email:
        await update.message.reply_text(smallcaps("Email cannot be empty. Please send a valid email."))
        return EMAIL_INPUT
    context.user_data['email'] = email
    await update.message.reply_text(smallcaps("Now send the OTP received on that email:"))
    return OTP_INPUT

async def otp_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    otp = update.message.text.strip()
    if not otp:
        await update.message.reply_text(smallcaps("OTP cannot be empty. Please send the OTP code."))
        return OTP_INPUT
    context.user_data['otp'] = otp
    await update.message.reply_text(smallcaps("Now set a 6‑digit Security Code (for future unbind/change):"))
    return SECURITY_INPUT

async def security_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sec = update.message.text.strip()
    if len(sec) != 6 or not sec.isdigit():
        await update.message.reply_text(smallcaps("Security code must be exactly 6 digits. Please try again."))
        return SECURITY_INPUT

    processing_msg = await update.message.reply_text(smallcaps("⏳ Pʀᴏᴄᴇssɪɴɢ..."))
    access_token = context.user_data.get('access_token')
    email = context.user_data.get('email')
    otp = context.user_data.get('otp')
    success, msg = bind_email_flow(access_token, email, otp, sec)
    await processing_msg.edit_text(msg)
    for key in ['access_token', 'email', 'otp']:
        context.user_data.pop(key, None)
    return ConversationHandler.END

async def unbind_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    if not code:
        await update.message.reply_text(smallcaps("Code cannot be empty. Please send the required code."))
        return UNBIND_CODE

    processing_msg = await update.message.reply_text(smallcaps("⏳ Pʀᴏᴄᴇssɪɴɢ..."))
    method = context.user_data.get('unbind_method')
    access_token = context.user_data.get('access_token')
    success, msg = unbind_email_flow(access_token, method, code)
    await processing_msg.edit_text(msg)
    context.user_data.pop('access_token', None)
    context.user_data.pop('unbind_method', None)
    return ConversationHandler.END

async def old_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    if not code:
        await update.message.reply_text(smallcaps("Code cannot be empty. Please send the required code."))
        return OLD_CODE
    context.user_data['old_code'] = code
    await update.message.reply_text(smallcaps("Now send the new email address:"))
    return NEW_EMAIL

async def new_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_email = update.message.text.strip()
    if not new_email:
        await update.message.reply_text(smallcaps("Email cannot be empty. Please send a valid email."))
        return NEW_EMAIL
    context.user_data['new_email'] = new_email
    await update.message.reply_text(smallcaps("Now send the OTP received on that new email:"))
    return NEW_OTP

async def new_otp_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_otp = update.message.text.strip()
    if not new_otp:
        await update.message.reply_text(smallcaps("OTP cannot be empty. Please send the OTP code."))
        return NEW_OTP

    processing_msg = await update.message.reply_text(smallcaps("⏳ Pʀᴏᴄᴇssɪɴɢ..."))
    access_token = context.user_data.get('access_token')
    method = context.user_data.get('change_method')
    old_code = context.user_data.get('old_code')
    new_email = context.user_data.get('new_email')
    success, msg = change_bind_flow(access_token, method, old_code, new_email, new_otp)
    await processing_msg.edit_text(msg)
    for key in ['access_token', 'change_method', 'old_code', 'new_email']:
        context.user_data.pop(key, None)
    return ConversationHandler.END

async def eat_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eat_input_text = update.message.text.strip()
    if not eat_input_text:
        await update.message.reply_text(smallcaps("Input cannot be empty. Please send EAT token or URL."))
        return EAT_INPUT

    processing_msg = await update.message.reply_text(smallcaps("⏳ Pʀᴏᴄᴇssɪɴɢ..."))
    success, msg, token = eat_to_access_token(eat_input_text)
    await processing_msg.edit_text(msg)
    return ConversationHandler.END

async def unsubscribe_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if not email:
        await update.message.reply_text(smallcaps("Email cannot be empty. Please send a valid email."))
        return UNSUBSCRIBE_EMAIL

    processing_msg = await update.message.reply_text(smallcaps("⏳ Pʀᴏᴄᴇssɪɴɢ..."))
    result = send_unsubscribe_otp(email)
    await processing_msg.edit_text(result)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(smallcaps("Operation cancelled. Use /start to begin again."))
    context.user_data.clear()
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        smallcaps("🤖 Garena Bind Tool Bot\nUse /start to see the menu.\nSend /cancel to abort.")
    )

# ============================================================================
#  ADMIN PANEL HANDLERS
# ============================================================================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📋 Usage Logs", callback_data="admin_usage")],
        [InlineKeyboardButton("⚠️ Error Logs", callback_data="admin_errors")],
        [InlineKeyboardButton("🔧 Maintenance Mode", callback_data="admin_maintenance")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")],
    ])
    await update.message.reply_text("⚙️ Admin Panel", reply_markup=keyboard)

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ Unauthorized.")
        return
    data = query.data
    if data == "admin_users":
        users = db_query("SELECT user_id, username, first_name, is_banned FROM users LIMIT 50", fetchall=True)
        if not users:
            text = "No users found."
        else:
            text = "👥 Users (first 50):\n" + "\n".join(
                [f"- {u[0]} | @{u[1] or 'N/A'} | {u[2]} | {'🚫 Banned' if u[3] else '✅ Active'}" for u in users]
            )
        await query.edit_message_text(text, reply_markup=admin_panel_keyboard())
    elif data == "admin_broadcast":
        await query.edit_message_text("📢 Send the message you want to broadcast to all users:")
        context.user_data['broadcast'] = True
        # We'll handle broadcast in a separate message handler
    elif data == "admin_usage":
        logs = db_query("SELECT user_id, command, timestamp FROM logs ORDER BY timestamp DESC LIMIT 20", fetchall=True)
        text = "📋 Recent Usage Logs:\n" + "\n".join(
            [f"- User {l[0]} | {l[1]} | {l[2]}" for l in logs]
        ) if logs else "No logs."
        await query.edit_message_text(text, reply_markup=admin_panel_keyboard())
    elif data == "admin_errors":
        errors = db_query("SELECT user_id, error, timestamp FROM errors ORDER BY timestamp DESC LIMIT 20", fetchall=True)
        text = "⚠️ Recent Errors:\n" + "\n".join(
            [f"- User {e[0]} | {e[1][:100]} | {e[2]}" for e in errors]
        ) if errors else "No errors."
        await query.edit_message_text(text, reply_markup=admin_panel_keyboard())
    elif data == "admin_maintenance":
        current = is_maintenance()
        set_maintenance(not current)
        status = "ON" if not current else "OFF"
        await query.edit_message_text(f"🔧 Maintenance mode set to {status}.", reply_markup=admin_panel_keyboard())
    elif data == "admin_back":
        await query.edit_message_text("⚙️ Admin Panel", reply_markup=admin_panel_keyboard())

def admin_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📋 Usage", callback_data="admin_usage")],
        [InlineKeyboardButton("⚠️ Errors", callback_data="admin_errors")],
        [InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")],
    ])

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.user_data.get('broadcast'):
        text = update.message.text
        if not text:
            await update.message.reply_text("❌ Empty message.")
            return
        users = db_query("SELECT user_id FROM users", fetchall=True)
        count = 0
        for (uid,) in users:
            try:
                await context.bot.send_message(uid, f"📢 <b>Broadcast from Admin:</b>\n{text}", parse_mode='HTML')
                count += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"Broadcast to {uid} failed: {e}")
        await update.message.reply_text(f"✅ Broadcast sent to {count} users.")
        context.user_data.pop('broadcast', None)
        log_command(update.effective_user.id, "broadcast", f"Sent to {count} users")
    else:
        await update.message.reply_text("No broadcast in progress. Use /admin to start.")

# ============================================================================
#  MAIN
# ============================================================================
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for all interactive commands
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_text),
            CallbackQueryHandler(button_handler, pattern="^(unbind_otp|unbind_sec|change_otp|change_sec)$"),
        ],
        states={
            TOKEN_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, token_input)],
            EMAIL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_input)],
            OTP_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, otp_input)],
            SECURITY_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, security_input)],
            UNBIND_METHOD: [CallbackQueryHandler(button_handler, pattern="^(unbind_otp|unbind_sec)$")],
            UNBIND_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, unbind_code_input)],
            CHANGE_METHOD: [CallbackQueryHandler(button_handler, pattern="^(change_otp|change_sec)$")],
            OLD_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, old_code_input)],
            NEW_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_email_input)],
            NEW_OTP: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_otp_input)],
            EAT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, eat_input)],
            UNSUBSCRIBE_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, unsubscribe_email_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(CommandHandler("help", help_command))
    # Broadcast message handler (after admin panel to catch broadcast messages)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message))

    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()