import json
import re
import requests
import sqlite3
import uuid
import random
import string
import os
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# === CONFIG ===
BOT_TOKEN = "8381209855:AAHoiCG1mKwnNoZr3DNi-licXaNWqTsVS4w"

# Channel Configuration
CHANNELS = [
    {"username": "@shadowmonarchjii", "url": "https://t.me/shadowmonarchjii", "name": "Main Channel"},
    {"username": "@nLTOKITLZJozYWFl", "url": "https://t.me/+nLTOKITLZJozYWFl", "name": "Second Channel"},
    {"username": "@C1FAIw62WVZmNGY1", "url": "https://t.me/+C1FAIw62WVZmNGY1", "name": "Third Channel"},
]

# Logger Group Configuration
LOGGER_GROUP_ID = -4951350354

# Channel join check - ENABLE KAR DIYA
FORCE_JOIN_CHECK = True  # Ab channel check enable hai

WELCOME_IMAGE = "https://i.ibb.co/NnsHbxb8/Ag-ACAg-UAAxk-BAAM-a-O-ks-Wahgns5-Fdol-Wl-UL01pz-HMAAp-QMaxt-Dm3l-XDLx-Jye-W1hp8-BAAMCAAN5-AAM2-BA.jpg"
WELCOME_TEXT = (
"╔═════════════════════════════════╗\n"
"║ 🔥 Welcome to 𓄂➤⃟♛𝐒𝐇𝐀𝐃𝐎𝐖 𝐌𝐎𝐍𝐀𝐑𝐂𝐇♛⃟➤ BOT 🔥 \n"
"╠═════════════════════════════════╣\n"
"║ Select an option below to search 💥\n"
"╠═════════════════════════════════╣                            \n"
"║  🛠️ Developed By: @shadowmonarchjii 💝  \n"
"╚═════════════════════════════════╝"
)

# --- APIs ---
APIS = {
    "mobile": [
        "https://number-to-information.vercel.app/fetch?key=NO-LOVE&num=",
        "https://num-info-gaurav.onrender.com/api/mobile?api_key=gaurav11&mobile=",
        "https://gaurav-info-paid.vercel.app/fetch?key=gauravpapa&num=",
        "https://mynkapi.amit1100941.workers.dev/?mobile={}&key=mynk01",
        "https://onlymynk-api-qq6u.vercel.app/api?key=mynk&type=mobile&term="
    ],
    "aadhar": [
        "https://rose-x-tool.vercel.app/fetch?key=@Ros3_x&aadhaar=",
        "https://aadhar-info-gaurav.onrender.com/api/aadhar?api_key=gaurav11&aadhar=",
        "https://apibymynk.vercel.app/fetch?key=onlymynk&aadhaar=",
        "https://onlymynk-api-qq6u.vercel.app/api?key=mynk&type=aadhar&term="
    ],
    "pak": [
        "https://seller-ki-mkc.taitanx.workers.dev/?aadhar=",
        "https://aadhar-info-gaurav.onrender.com/api/aadhar?api_key=gaurav11&aadhar=",
        "https://onlymynk-api-qq6u.vercel.app/api?key=mynk&type=aadhar&term="
    ],
    "vehicle": [
        "https://vehicle-2-info.vercel.app/rose-x?vehicle_no=",
        "https://veerulookup.onrender.com/search_vehicle?rc="
    ],
    "pincode": [
        "https://veerulookup.onrender.com/search_pincode?pincode="
    ],
    "ifsc": [
        "https://veerulookup.onrender.com/search_ifsc?ifsc="
    ],
    "id_number": [
        "https://onlymynk-api-qq6u.vercel.app/api?key=mynk&type=id_number&term="
    ]
}

# Points system
POINTS_PER_SEARCH = 1
POINTS_PER_REFERRAL = 2
DAILY_BONUS_POINTS = 1

# Developer contact
DEVELOPER_CONTACT_URL = "https://t.me/shadowmonarchjii"  
DEVELOPER_TAG = "Developer ➜ @shadowmonarchjii"

# Track pending input type per user
USER_PENDING_TYPE = {}

# Track users who have joined channels
JOINED_USERS = set()

# Blocked numbers list
BLOCKED_NUMBERS = {
    "9798673XXX": "❌ This number is blocked from searching."
}

# Admin IDs
ADMIN_IDS = [7623647710, 6969001744]

# Database setup
def init_db():
    if os.path.exists('bot_data.db'):
        os.remove('bot_data.db')
        print("Old database deleted")
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            points INTEGER DEFAULT 0,
            referred_by INTEGER,
            last_bonus_date TEXT,
            join_date TEXT,
            total_searches INTEGER DEFAULT 0,
            channels_joined BOOLEAN DEFAULT FALSE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE redeem_codes (
            code TEXT PRIMARY KEY,
            points INTEGER,
            created_by INTEGER,
            used_by INTEGER DEFAULT NULL,
            used_date TEXT,
            created_date TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            search_type TEXT,
            query TEXT,
            result TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("New database created with correct schema!")

def create_sample_redeem_codes():
    """Sample redeem codes create karta hai"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    sample_codes = [
        ("WELCOME10", 10, ADMIN_IDS[0]),
        ("NEWUSER50", 50, ADMIN_IDS[0]),
        ("BONUS100", 100, ADMIN_IDS[0]),
        ("VIP500", 500, ADMIN_IDS[0]),
        ("PREMIUM1000", 1000, ADMIN_IDS[0]),
        ("FREE5", 5, ADMIN_IDS[0]),
        ("STARTER20", 20, ADMIN_IDS[0]),
        ("PRO200", 200, ADMIN_IDS[0])
    ]
    
    for code, points, admin_id in sample_codes:
        try:
            cursor.execute('''
                INSERT INTO redeem_codes (code, points, created_by, created_date, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', (code, points, admin_id, datetime.now().isoformat(), True))
            print(f"✓ Created redeem code: {code} - {points} points")
        except Exception as e:
            print(f"✗ Error creating code {code}: {e}")
    
    conn.commit()
    conn.close()
    print("✓ Sample redeem codes created successfully!")

# User management functions
def get_user(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'user_id': user[0],
            'username': user[1],
            'first_name': user[2],
            'points': user[3],
            'referred_by': user[4],
            'last_bonus_date': user[5],
            'join_date': user[6],
            'total_searches': user[7],
            'channels_joined': user[8]
        }
    return None

def create_user(user_id, username, first_name, referred_by=None):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, points, referred_by, join_date, channels_joined)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, 0, referred_by, datetime.now().isoformat(), False))
    conn.commit()
    conn.close()

def mark_channels_joined(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET channels_joined = TRUE WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    JOINED_USERS.add(user_id)

def update_points(user_id, points_change):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (points_change, user_id))
    conn.commit()
    conn.close()

def increment_search_count(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET total_searches = total_searches + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_points(user_id):
    user = get_user(user_id)
    return user['points'] if user else 0

def check_daily_bonus(user_id):
    user = get_user(user_id)
    if not user:
        return False
    
    today = datetime.now().date().isoformat()
    if user['last_bonus_date'] != today:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET points = points + ?, last_bonus_date = ? WHERE user_id = ?', 
                      (DAILY_BONUS_POINTS, today, user_id))
        conn.commit()
        conn.close()
        return True
    return False

# NEW: Get all users for broadcast
def get_all_users():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

# NEW: Get user stats for admin
def get_user_stats():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE channels_joined = TRUE')
    joined_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(points) FROM users')
    total_points = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT SUM(total_searches) FROM users')
    total_searches = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM search_logs')
    total_logs = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'joined_users': joined_users,
        'total_points': total_points,
        'total_searches': total_searches,
        'total_logs': total_logs
    }

# Redeem code functions
def create_redeem_code(points, created_by):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO redeem_codes (code, points, created_by, created_date, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (code, points, created_by, datetime.now().isoformat(), True))
        conn.commit()
        return code
    except Exception as e:
        return None
    finally:
        conn.close()

def redeem_code(code, user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM redeem_codes WHERE code = ? AND is_active = TRUE AND used_by IS NULL', (code,))
        redeem_data = cursor.fetchone()
        
        if redeem_data:
            points = redeem_data[1]
            cursor.execute('UPDATE redeem_codes SET used_by = ?, used_date = ? WHERE code = ?', 
                          (user_id, datetime.now().isoformat(), code))
            cursor.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (points, user_id))
            conn.commit()
            return points
        else:
            return 0
    except Exception as e:
        return 0
    finally:
        conn.close()

def get_all_redeem_codes():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT code, points, created_by, used_by FROM redeem_codes WHERE is_active = TRUE ORDER BY points DESC')
    codes = cursor.fetchall()
    conn.close()
    return codes

# Logger functions
def log_search(user_id, search_type, query, result):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO search_logs (user_id, search_type, query, result, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, search_type, query, json.dumps(result), datetime.now().isoformat()))
    conn.commit()
    conn.close()

async def send_log_to_group(context, log_message):
    try:
        await context.bot.send_message(
            chat_id=LOGGER_GROUP_ID,
            text=log_message,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"Logger error: {e}")

# ---------- helpers ----------
def main_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("👭👬 Aadhar to Family", callback_data="aadhar")],
        [InlineKeyboardButton("📞 Mobile Number", callback_data="mobile")],
        [InlineKeyboardButton("🧍🏻 Aadhar Number", callback_data="pak")],
        [InlineKeyboardButton("🚗 Vehicle Number", callback_data="vehicle")],
        [InlineKeyboardButton("📍 Pincode", callback_data="pincode")],
        [InlineKeyboardButton("🏦 IFSC Code", callback_data="ifsc")],
        [InlineKeyboardButton("🆔 ID Number", callback_data="id_number")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("📊 My Points", callback_data="my_points")],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")],
        [InlineKeyboardButton("💰 Redeem Code", callback_data="redeem_code")],
        [InlineKeyboardButton("🪪 Developer Contact", url=DEVELOPER_CONTACT_URL)], 
    ]
    return InlineKeyboardMarkup(keyboard)

def result_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("↩️ Back to Main Menu", callback_data="main_menu")],
        [InlineKeyboardButton("🪪 Developer Contact", url=DEVELOPER_CONTACT_URL)], 
    ]
    return InlineKeyboardMarkup(keyboard)

def channels_markup():
    keyboard = []
    for channel in CHANNELS:
        keyboard.append([InlineKeyboardButton(f"✅ Join {channel['name']}", url=channel['url'])])
    keyboard.append([InlineKeyboardButton("✅ I've Joined All", callback_data="check_joined")])
    return InlineKeyboardMarkup(keyboard)

def clean_number(number: str) -> str:
    return re.sub(r"[^\d+]", "", number or "")

def is_blocked_number(number: str):
    number_clean = clean_number(number)
    for blocked, response in BLOCKED_NUMBERS.items():
        blocked_clean = clean_number(str(blocked))
        if blocked_clean in number_clean or number_clean.endswith(blocked_clean):
            return response
    return False

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    # Check if user has manually confirmed join
    if user_id in JOINED_USERS:
        return True
        
    user = get_user(user_id)
    if user and user.get('channels_joined'):
        return True
        
    # For private channels, we rely on manual confirmation
    return False

async def check_and_block_if_not_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
        
    # If no channels configured or force check disabled, allow access
    if not CHANNELS or not FORCE_JOIN_CHECK:
        return True
        
    is_joined = await check_subscription(user.id, context)
    if not is_joined:
        # Pehle channel join message show karo
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔒 <b>CHANNEL JOIN REQUIRED</b> 🔒\n\n"
                 "📢 <b>To use this bot, you must join our channels first!</b>\n\n"
                 "👇 <b>Join all channels below and then click 'I've Joined All':</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=channels_markup()
        )
        return False
    return True

def get_referral_link(user_id):
    return f"https://t.me/osint_shadow_op_robot?start=ref{user_id}"

# Process number function
async def process_number(chat_id: int, number_type: str, number: str, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    user = get_user(user_id)
    
    # Check points
    user_points = get_points(user_id)
    if user_points < POINTS_PER_SEARCH:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"❌ Insufficient points! You need {POINTS_PER_SEARCH} point per search. You have {user_points} points.\n\nUse /refer to get more points.",
            reply_markup=main_inline_keyboard()
        )
        return

    blocked_response = is_blocked_number(number)
    if blocked_response:
        await context.bot.send_message(chat_id=chat_id, text=blocked_response, reply_markup=main_inline_keyboard())
        return

    number_clean = clean_number(number)
    
    # Input Validation
    validation_rules = {
        "mobile": (10, "10 digits"),
        "aadhar": (12, "12 digits"),
        "pak": (12, "12 digits"),
        "pincode": (6, "6 digits"),
        "ifsc": (11, "11 characters"),
        "id_number": (1, "at least 1 character"),
        "vehicle": (1, "at least 1 character")
    }
    
    if number_type in validation_rules:
        min_length, description = validation_rules[number_type]
        if len(number_clean) < min_length:
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"❌ Invalid {number_type} number. Must be {description}.",
                reply_markup=main_inline_keyboard()
            )
            return
    
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Processing your request...", parse_mode=ParseMode.HTML)

    # Log search start
    log_message = f"🔍 <b>New Search Request</b>\n\n"
    log_message += f"👤 <b>User:</b> {user['first_name']}\n"
    log_message += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
    log_message += f"📛 <b>Username:</b> @{user['username'] if user['username'] else 'N/A'}\n"
    log_message += f"📊 <b>Type:</b> {number_type.upper()}\n"
    log_message += f"🔢 <b>Query:</b> <code>{number}</code>\n"
    log_message += f"⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
    
    await send_log_to_group(context, log_message)

    # Try multiple APIs
    api_urls = APIS.get(number_type, [])
    data = {"error": "No response from any API"}
    api_used = "None"
    
    for api_url in api_urls:
        try:
            if "{}" in api_url:
                formatted_url = api_url.format(number_clean)
            else:
                formatted_url = api_url + quote_plus(number_clean)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            resp = requests.get(formatted_url, headers=headers, timeout=15)
            
            if resp.status_code == 200:
                try:
                    api_data = resp.json()
                    if api_data and (isinstance(api_data, dict) or isinstance(api_data, list)):
                        if isinstance(api_data, dict) and api_data.get('error'):
                            continue
                        data = api_data
                        api_used = api_url.split('/')[2] if '/' in api_url else api_url
                        break
                except json.JSONDecodeError:
                    if resp.text.strip():
                        data = {"response": resp.text}
                        api_used = api_url.split('/')[2] if '/' in api_url else api_url
                        break
        except Exception as e:
            continue

    # Deduct points after search attempt
    update_points(user_id, -POINTS_PER_SEARCH)
    increment_search_count(user_id)

    # Log search result
    result_log = f"✅ <b>Search Result</b>\n\n"
    result_log += f"👤 <b>User:</b> {user['first_name']}\n"
    result_log += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
    result_log += f"📛 <b>Username:</b> @{user['username'] if user['username'] else 'N/A'}\n"
    result_log += f"📊 <b>Type:</b> {number_type.upper()}\n"
    result_log += f"🔢 <b>Query:</b> <code>{number}</code>\n"
    result_log += f"🌐 <b>API Used:</b> {api_used}\n"
    result_log += f"📈 <b>Result:</b> {'Success' if 'error' not in str(data).lower() else 'Failed'}\n"
    result_log += f"⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
    
    await send_log_to_group(context, result_log)
    
    # Save to database log
    log_search(user_id, number_type, number, data)

    developer_credit = f"\n\n{DEVELOPER_TAG}"
    
    # Format result better
    if isinstance(data, dict) and data.get('error'):
        result_text = f"❌ <b>No data found for {number_type}: {number}</b>\n\n"
        result_text += f"<i>All APIs returned no results. Please try with different information.</i>"
    else:
        result_text = f"<b>🔍 Result for {number_type.upper()}: {number}</b>\n\n"
        result_text += f"<pre>{json.dumps(data, indent=2, ensure_ascii=False)}</pre>"
    
    final_text = f"{result_text}\n\n💎 Points used: {POINTS_PER_SEARCH}{developer_credit}"
    reply_markup = result_inline_keyboard()

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=loading_msg.message_id,
            text=final_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except:
        await context.bot.send_message(
            chat_id=chat_id,
            text=final_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

# ---------- NEW BROADCAST COMMAND ----------
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Admin check
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only command.")
        return
        
    if not context.args:
        await update.message.reply_text(
            "📢 <b>Broadcast Command</b>\n\n"
            "Usage: <code>/broadcast your message here</code>\n\n"
            "Example: <code>/broadcast Hello users! New features added!</code>",
            parse_mode=ParseMode.HTML
        )
        return
        
    message_text = ' '.join(context.args)
    all_users = get_all_users()
    
    if not all_users:
        await update.message.reply_text("❌ No users found in database.")
        return
        
    # Confirmation message
    confirm_msg = await update.message.reply_text(
        f"📢 <b>Broadcast Confirmation</b>\n\n"
        f"📝 <b>Message:</b> {message_text}\n\n"
        f"👥 <b>Total Users:</b> {len(all_users)}\n\n"
        f"⚠️ <b>Are you sure you want to send this broadcast?</b>\n"
        f"Reply with 'YES' to confirm or 'NO' to cancel.",
        parse_mode=ParseMode.HTML
    )
    
    # Store broadcast data in context for confirmation
    context.user_data['pending_broadcast'] = {
        'message': message_text,
        'users': all_users,
        'confirm_msg_id': confirm_msg.message_id
    }

# Broadcast confirmation handler
async def broadcast_confirmation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
        
    pending_broadcast = context.user_data.get('pending_broadcast')
    if not pending_broadcast:
        return
        
    user_response = update.message.text.strip().upper()
    
    if user_response == 'YES':
        message_text = pending_broadcast['message']
        all_users = pending_broadcast['users']
        
        # Delete confirmation message
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=pending_broadcast['confirm_msg_id']
            )
        except:
            pass
            
        # Start broadcast
        progress_msg = await update.message.reply_text(
            f"🔄 <b>Starting Broadcast...</b>\n\n"
            f"📤 Sent: 0/{len(all_users)}\n"
            f"✅ Successful: 0\n"
            f"❌ Failed: 0",
            parse_mode=ParseMode.HTML
        )
        
        successful = 0
        failed = 0
        
        for index, user_id in enumerate(all_users, 1):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 <b>Announcement from Admin</b>\n\n{message_text}\n\n{DEVELOPER_TAG}",
                    parse_mode=ParseMode.HTML
                )
                successful += 1
            except Exception as e:
                failed += 1
                
            # Update progress every 10 messages
            if index % 10 == 0 or index == len(all_users):
                try:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=progress_msg.message_id,
                        text=f"🔄 <b>Broadcast Progress</b>\n\n"
                             f"📤 Sent: {index}/{len(all_users)}\n"
                             f"✅ Successful: {successful}\n"
                             f"❌ Failed: {failed}",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
                    
            # Small delay to avoid rate limits
            await asyncio.sleep(0.1)
            
        # Final result
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=progress_msg.message_id,
            text=f"✅ <b>Broadcast Completed!</b>\n\n"
                 f"📊 <b>Final Results:</b>\n"
                 f"• Total Users: {len(all_users)}\n"
                 f"• ✅ Successful: {successful}\n"
                 f"• ❌ Failed: {failed}\n"
                 f"• 📊 Success Rate: {(successful/len(all_users))*100:.1f}%",
            parse_mode=ParseMode.HTML
        )
        
        # Log broadcast
        broadcast_log = f"📢 <b>Broadcast Sent</b>\n\n"
        broadcast_log += f"👤 <b>Admin:</b> {update.effective_user.first_name}\n"
        broadcast_log += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        broadcast_log += f"📝 <b>Message:</b> {message_text[:100]}...\n"
        broadcast_log += f"📊 <b>Stats:</b> {successful}✅ {failed}❌\n"
        broadcast_log += f"⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        await send_log_to_group(context, broadcast_log)
        
    elif user_response == 'NO':
        await update.message.reply_text("❌ Broadcast cancelled.")
    else:
        await update.message.reply_text("❌ Please reply with 'YES' to confirm or 'NO' to cancel.")
        
    # Clear pending broadcast
    context.user_data.pop('pending_broadcast', None)

# NEW: Admin stats command
async def admin_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only command.")
        return
        
    stats = get_user_stats()
    
    stats_text = f"📊 <b>Bot Statistics</b>\n\n"
    stats_text += f"👥 <b>Total Users:</b> {stats['total_users']}\n"
    stats_text += f"✅ <b>Joined Channels:</b> {stats['joined_users']}\n"
    stats_text += f"💎 <b>Total Points Distributed:</b> {stats['total_points']}\n"
    stats_text += f"🔍 <b>Total Searches:</b> {stats['total_searches']}\n"
    stats_text += f"📝 <b>Search Logs:</b> {stats['total_logs']}\n\n"
    
    # Active users (last 7 days)
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM search_logs WHERE timestamp > ?', (week_ago,))
    active_users = cursor.fetchone()[0]
    conn.close()
    
    stats_text += f"🎯 <b>Active Users (7 days):</b> {active_users}"
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

# ---------- handlers ----------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    # Create user if not exists
    create_user(user.id, user.username, user.first_name)
    
    # Handle referral
    if args and args[0].startswith('ref'):
        try:
            referrer_id = int(args[0][3:])
            if referrer_id != user.id:
                user_data = get_user(user.id)
                if user_data and not user_data['referred_by']:
                    conn = sqlite3.connect('bot_data.db')
                    cursor = conn.cursor()
                    cursor.execute('UPDATE users SET referred_by = ? WHERE user_id = ?', (referrer_id, user.id))
                    cursor.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (POINTS_PER_REFERRAL, referrer_id))
                    conn.commit()
                    conn.close()
        except ValueError:
            pass
    
    # Log user start
    log_message = f"🆕 <b>New User Started Bot</b>\n\n"
    log_message += f"👤 <b>User:</b> {user.first_name}\n"
    log_message += f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
    log_message += f"📛 <b>Username:</b> @{user.username if user.username else 'N/A'}\n"
    log_message += f"📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    await send_log_to_group(context, log_message)
    
    # IMPORTANT: Channel join check karo - AB CHANNEL JOIN MESSAGE AYEGA
    if not await check_and_block_if_not_joined(update, context):
        return  # Yahan return karo agar user ne join nahi kiya
        
    # Agar user ne join kar liya hai, toh main menu show karo
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=main_inline_keyboard(),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # FIX: Query timeout error handle karo
    try:
        await query.answer()
    except Exception as e:
        print(f"Query answer error: {e}")
    
    user_id = query.from_user.id
    user = get_user(user_id)

    log_message = f"🔄 <b>Button Clicked</b>\n\n"
    log_message += f"👤 <b>User:</b> {user['first_name'] if user else 'Unknown'}\n"
    log_message += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
    log_message += f"📛 <b>Username:</b> @{user['username'] if user and user['username'] else 'N/A'}\n"
    log_message += f"🔘 <b>Button:</b> {query.data}\n"
    log_message += f"⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
    
    await send_log_to_group(context, log_message)

    if query.data == "check_joined":
        # User ne manually confirm kiya ki join kar liya
        mark_channels_joined(user_id)
        JOINED_USERS.add(user_id)
        
        await query.message.edit_text(
            "✅ <b>Thank you for joining our channels!</b>\n\n"
            "🎉 <b>You can now use all bot features.</b>\n\n"
            "👇 <b>Click the button below to start using the bot:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start Using Bot", callback_data="main_menu")]
            ])
        )
        return
    
    if query.data == "redeem_code":
        await query.message.reply_text(
            "💰 <b>Redeem Code</b>\n\n"
            "To redeem a code, use the command:\n"
            "<code>/redeem CODE_HERE</code>\n\n"
            "Example: <code>/redeem WELCOME10</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # IMPORTANT: Har button ke liye channel check karo
    if not await check_and_block_if_not_joined(update, context):
        return
    
    if query.data in ["aadhar", "mobile", "pak", "vehicle", "pincode", "ifsc", "id_number"]:
        USER_PENDING_TYPE[user_id] = query.data
        prompt = {
            "aadhar": "🔢 Please enter 12-digit Aadhar number:",
            "mobile": "📱 Please enter 10-digit mobile number:",
            "pak": "🆔 Please enter 12-digit Aadhar number:",
            "vehicle": "🚗 Please enter Vehicle Number:",
            "pincode": "📍 Please enter 6-digit Pincode:",
            "ifsc": "🏦 Please enter 11-character IFSC Code:",
            "id_number": "🪪 Please enter ID Number:"
        }
        await query.message.reply_text(prompt[query.data])
    
    elif query.data == "main_menu":
        try:
            await query.message.delete()
        except:
            pass
            
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=WELCOME_IMAGE,
            caption=WELCOME_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=main_inline_keyboard(),
        )
    
    elif query.data == "daily_bonus":
        if check_daily_bonus(user_id):
            bonus_log = f"🎁 <b>Daily Bonus Claimed</b>\n\n"
            bonus_log += f"👤 <b>User:</b> {user['first_name']}\n"
            bonus_log += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            bonus_log += f"📛 <b>Username:</b> @{user['username'] if user['username'] else 'N/A'}\n"
            bonus_log += f"💰 <b>Points:</b> +{DAILY_BONUS_POINTS}\n"
            bonus_log += f"⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
            
            await send_log_to_group(context, bonus_log)
            await query.message.reply_text(f"🎉 You received {DAILY_BONUS_POINTS} daily bonus points!")
        else:
            await query.message.reply_text("❌ You've already claimed your daily bonus today. Come back tomorrow!")
    
    elif query.data == "my_points":
        points = get_points(user_id)
        await query.message.reply_text(f"💎 Your current points: {points}\n\nEach search costs {POINTS_PER_SEARCH} point.")
    
    elif query.data == "refer":
        ref_link = get_referral_link(user_id)
        await query.message.reply_text(
            f"👥 **Referral Program** 👥\n\n"
            f"🔗 Your referral link:\n`{ref_link}`\n\n"
            f"💎 Earn {POINTS_PER_REFERRAL} points for each friend who joins!\n"
            f"📱 Share your link and start earning!",
            parse_mode=ParseMode.MARKDOWN
        )

# Message router
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # IMPORTANT: Har message ke liye channel check karo
    if not await check_and_block_if_not_joined(update, context):
        return

    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    
    # Check for broadcast confirmation
    if user_id in ADMIN_IDS and context.user_data.get('pending_broadcast'):
        await broadcast_confirmation_handler(update, context)
        return
    
    if user_id in USER_PENDING_TYPE:
        number_type = USER_PENDING_TYPE.pop(user_id)
        await process_number(update.effective_chat.id, number_type, text, context, user_id)
        return
        
    await update.message.reply_text(
        "Please select an option from the menu below.",
        reply_markup=main_inline_keyboard()
    )

# Other handlers...
async def redeem_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not context.args:
        await update.message.reply_text(
            "💰 <b>Redeem Code</b>\n\n"
            "Usage: <code>/redeem CODE_HERE</code>\n\n"
            "Example: <code>/redeem WELCOME10</code>",
            parse_mode=ParseMode.HTML
        )
        return
    
    code = context.args[0].upper().strip()
    points_added = redeem_code(code, user_id)
    
    if points_added > 0:
        redeem_log = f"💰 <b>Redeem Code Used</b>\n\n"
        redeem_log += f"👤 <b>User:</b> {user['first_name']}\n"
        redeem_log += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        redeem_log += f"📛 <b>Username:</b> @{user['username'] if user['username'] else 'N/A'}\n"
        redeem_log += f"🔢 <b>Code:</b> {code}\n"
        redeem_log += f"💰 <b>Points:</b> +{points_added}\n"
        redeem_log += f"⏰ <b>Time:</b> {datetime.now().strftime('%H:%M:%S')}"
        
        await send_log_to_group(context, redeem_log)
        
        new_balance = get_points(user_id)
        await update.message.reply_text(
            f"🎉 <b>Successfully redeemed {points_added} points!</b>\n\n"
            f"💰 <b>New Balance:</b> {new_balance} points",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("❌ Invalid or already used redeem code!")

async def create_redeem_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only command.")
        return
        
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /createredeem <points>")
        return
        
    try:
        points = int(context.args[0])
        code = create_redeem_code(points, user_id)
        
        if code:
            await update.message.reply_text(
                f"🎉 Redeem code created!\nCode: `{code}`\nPoints: {points}",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text("❌ Failed to create redeem code.")
    except ValueError:
        await update.message.reply_text("❌ Points must be a valid number.")

async def points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    points = get_points(user_id)
    await update.message.reply_text(f"💎 Your current points: {points}\n\nEach search costs {POINTS_PER_SEARCH} point.")

async def refer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_link = get_referral_link(user_id)
    await update.message.reply_text(
        f"👥 **Referral Program** 👥\n\n"
        f"🔗 Your referral link:\n`{ref_link}`\n\n"
        f"💎 Earn {POINTS_PER_REFERRAL} points for each friend who joins!\n"
        f"📱 Share your link and start earning!",
        parse_mode=ParseMode.MARKDOWN
    )

# ---------- main ----------
def main():
    init_db()
    create_sample_redeem_codes()
    
    # Network settings for Railway deployment
    import httpx
    import httpcore
    
    # Configure better timeout settings
    request_kwargs = {
        'connect_timeout': 30.0,
        'read_timeout': 30.0,
        'write_timeout': 30.0,
        'pool_timeout': 30.0,
    }
    
    application = ApplicationBuilder().token(BOT_TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).pool_timeout(30).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("points", points_handler))
    application.add_handler(CommandHandler("refer", refer_handler))
    application.add_handler(CommandHandler("redeem", redeem_handler))
    application.add_handler(CommandHandler("createredeem", create_redeem_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    application.add_handler(CommandHandler("stats", admin_stats_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 BOT STARTED WITH CHANNEL JOIN SYSTEM!")
    print("📢 Users must join channels before using the bot")
    print("🎯 Broadcast command added for admins")
    print("📊 Admin stats command available")
    
    # Better error handling for polling
    try:
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            poll_interval=1,
            timeout=30,
            drop_pending_updates=True
        )
    except Exception as e:
        print(f"Bot polling error: {e}")
        print("Restarting bot in 10 seconds...")
        import time
        time.sleep(10)
        main()  # Restart bot

if __name__ == "__main__":
    main()
