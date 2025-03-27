import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    Filters,
    CallbackContext
)
import asyncio
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import aiohttp
from pddikti_api import login_pddikti, search_student, get_student_detail

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get tokens from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '0'))

# File untuk menyimpan data pengguna yang diizinkan
ALLOWED_USERS_FILE = "allowed_users.json"

def load_allowed_users():
    """Load allowed users from JSON file"""
    try:
        print("\n=== Loading Allowed Users ===")
        if not os.path.exists(ALLOWED_USERS_FILE):
            print(f"Warning: {ALLOWED_USERS_FILE} does not exist")
            return {"users": []}
            
        with open(ALLOWED_USERS_FILE, 'r') as f:
            data = json.load(f)
            print(f"Raw data loaded: {json.dumps(data, indent=2)}")
            
            # Ensure data has correct structure
            if isinstance(data, dict) and "users" in data:
                print("Data has correct dictionary structure")
                return data
            elif isinstance(data, list):
                print("Converting list to dictionary structure")
                return {"users": data}
            else:
                print("Invalid data structure, returning empty user list")
                return {"users": []}
                
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {str(e)}")
        return {"users": []}
    except Exception as e:
        print(f"Error loading allowed users: {str(e)}")
        return {"users": []}

def is_user_allowed(user_id):
    """Check if user is allowed to use the bot"""
    try:
        allowed_users = load_allowed_users()
        print(f"\n=== Checking User Permission ===")
        print(f"User ID: {user_id}")
        print(f"Allowed Users: {json.dumps(allowed_users, indent=2)}")
        
        if not isinstance(allowed_users, dict):
            print("Error: allowed_users is not a dictionary")
            return False
            
        if "users" not in allowed_users:
            print("Error: 'users' key not found in allowed_users")
            return False
            
        is_allowed = any(user['id'] == user_id for user in allowed_users.get('users', []))
        print(f"Is User Allowed: {is_allowed}")
        return is_allowed
        
    except Exception as e:
        print(f"Error in is_user_allowed: {str(e)}")
        return False

def check_user_permission(update: Update) -> bool:
    """Check if user has permission to use the bot"""
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return False
    return True

async def send_notification_to_admin(user_id: int, username: str, message: str):
    """Send notification to admin about user activity"""
    try:
        print("\n=== Sending Notification ===")
        print(f"ADMIN_BOT_TOKEN: {ADMIN_BOT_TOKEN[:10]}...")
        print(f"ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
        
        # Validate tokens and chat ID
        if not ADMIN_BOT_TOKEN:
            print("Error: ADMIN_BOT_TOKEN is empty")
            return
        if not ADMIN_CHAT_ID:
            print("Error: ADMIN_CHAT_ID is empty")
            return
            
        notification = (
            f"📱 *Pesan Baru dari User*\n\n"
            f"⏰ Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"👤 User ID: `{user_id}`\n"
            f"Username: @{username}\n"
            f"Pesan: {message}"
        )
        
        url = f"https://api.telegram.org/bot{ADMIN_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_CHAT_ID,
            "text": notification,
            "parse_mode": "Markdown"
        }
        
        print(f"Sending request to: {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        # Use aiohttp with timeout
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(url, json=data) as response:
                    print(f"Response status code: {response.status}")
                    response_text = await response.text()
                    print(f"Response text: {response_text}")
                    
                    if response.status != 200:
                        logger.error(f"Failed to send notification: {response_text}")
                        print(f"Error sending notification: {response_text}")
                    else:
                        print(f"Notification sent successfully to admin")
            except aiohttp.ClientError as e:
                print(f"Network error: {str(e)}")
                logger.error(f"Network error sending notification: {str(e)}")
            except asyncio.TimeoutError as e:
                print(f"Timeout error: {str(e)}")
                logger.error(f"Timeout error sending notification: {str(e)}")
            
    except Exception as e:
        logger.error(f"Failed to send notification to admin: {str(e)}")
        print(f"Error sending notification: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def handle_message(update: Update, context: CallbackContext):
    """Handle all incoming messages"""
    try:
        print("\n=== Handling Message ===")
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        print(f"User ID: {user_id}")
        print(f"Username: {username}")
        
        # Get message type and content
        message = update.message
        if not message:
            print("Error: No message found in update")
            return
            
        # Check if we're waiting for search input
        if context.user_data.get('waiting_for_search'):
            # Clear the waiting flag
            context.user_data.pop('waiting_for_search', None)
            
            # Get the search keyword
            keyword = message.text
            
            # Show initial progress bar
            progress_message = show_progress(update, context, 5)
            
            # This will be handled synchronously for now due to compatibility
            # The actual search functionality might need to be modified
            # to work with the older version without async/await
            
        else:
            # Handle other types of messages as before
            if message.photo:
                message_text = f"[Photo] {message.caption if message.caption else 'No caption'}"
            elif message.document:
                message_text = f"[Document] {message.document.file_name}"
            elif message.voice:
                message_text = "[Voice Message]"
            elif message.video:
                message_text = f"[Video] {message.caption if message.caption else 'No caption'}"
            elif message.sticker:
                message_text = f"[Sticker] {message.sticker.emoji}"
            elif message.location:
                message_text = f"[Location] {message.location.latitude}, {message.location.longitude}"
            elif message.contact:
                message_text = f"[Contact] {message.contact.first_name} {message.contact.last_name}"
            elif message.animation:
                message_text = "[Animation]"
            elif message.audio:
                message_text = f"[Audio] {message.audio.title if message.audio.title else 'No title'}"
            else:
                message_text = message.text if message.text else "Unknown message"
            
            print(f"Message text: {message_text}")
            
            # Check permission - we can do this synchronously for now
            if not check_user_permission(update):
                return
            
    except Exception as e:
        print(f"Error in handle_message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def cleanup_user_session(context: CallbackContext):
    """Cleanup user session when done"""
    if 'session' in context.user_data:
        # This would normally be async, but we'll handle it synchronously for now
        context.user_data.pop('session', None)

def start(update: Update, context: CallbackContext):
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    # Cleanup any existing session
    cleanup_user_session(context)
    
    # Send a simple welcome message for now
    update.message.reply_text(
        "🔍 I can search for any student data across Indonesia\n\n"
        "📝 How to use:\n"
        "• Search by name: /cari [nama]\n"
        "• Search by NIM: /cari [nim]\n\n"
        "📌 Examples:\n"
        "• /cari Ahmad Fauzi\n"
        "• /cari 2020123456\n"
        "• /cari Siti Nurhaliza\n"
        "• /cari 2020987654\n\n"
        "💡 Tips:\n"
        "• You can search using full name or NIM\n"
        "• Results will show student's complete information\n"
        "• Click on any result to see more details\n\n"
        "👨‍💻 Developed by Nant\n"
        "✈️ Contact: @nant12_bot"
    )

def show_progress(update: Update, context: CallbackContext, total_steps: int):
    """Show progress bar during search"""
    progress_message = update.message.reply_text("🔍 Mencari data mahasiswa...\n[▱▱▱▱▱▱▱▱▱▱] 0%")
    return progress_message

def update_progress(progress_message, progress: int):
    """Update progress bar with given percentage"""
    bar = "▰" * progress + "▱" * (10 - progress)
    progress_message.edit_text(f"🔍 Mencari data mahasiswa...\n[{bar}] {progress*10}%")

def search(update: Update, context: CallbackContext):
    """Handle /search command"""
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        print(f"\n=== Handling Search Command ===")
        print(f"User ID: {user_id}")
        print(f"Username: {username}")
        
        # Check permission after /cari command
        allowed_users = load_allowed_users()
        print(f"Loaded allowed users: {json.dumps(allowed_users, indent=2)}")
        
        is_allowed = any(user.get('id') == user_id for user in allowed_users.get('users', []))
        print(f"Is user {user_id} allowed: {is_allowed}")
        
        if not is_allowed:
            print(f"Access denied for user {user_id}")
            # Send restriction message to user
            restriction_message = (
                "⚠️ <b>Akses Terbatas</b>\n\n"
                "Maaf, Anda belum memiliki akses untuk menggunakan fitur ini.\n"
                "Silakan hubungi admin untuk mendapatkan akses.\n\n"
                "Contact: @nant12_bot"
            )
            update.message.reply_text(
                restriction_message,
                parse_mode='HTML'
            )
            return
        
        if not context.args:
            update.message.reply_text(
                "Silakan masukkan nama mahasiswa yang ingin dicari.\n"
                "Contoh: /cari John Doe",
                reply_markup=ForceReply(selective=True)
            )
            return

        # Get search keyword
        keyword = " ".join(context.args)
        print(f"Search keyword: {keyword}")
        
        # Show initial progress - simplified for non-async version
        progress_message = show_progress(update, context, 5)
        update.message.reply_text("Pencarian melalui bot sedang dalam perbaikan. Silakan tunggu update selanjutnya.")
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

def show_loading(update: Update, context: CallbackContext, message: str):
    """Show loading animation"""
    loading_message = update.callback_query.message.reply_text(f"⏳ {message}")
    return loading_message

def button_callback(update: Update, context: CallbackContext):
    """Handle button callbacks"""
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    
    # Check permission for button callbacks
    if not is_user_allowed(user_id):
        query.message.edit_text(
            "⚠️ *Akses Terbatas*\n\n"
            "Maaf, Anda belum memiliki akses untuk menggunakan fitur ini.\n"
            "Silakan hubungi admin untuk mendapatkan akses.\n\n"
            "📞 Contact: @nant12_bot",
            parse_mode='Markdown'
        )
        return
    
    username = query.from_user.username or "Unknown"
    
    try:
        if query.data.startswith("mhs_"):
            # Simplified for non-async version
            query.message.edit_text("Fitur pencarian detail sedang dalam perbaikan. Silakan tunggu update selanjutnya.", parse_mode='Markdown')
            
        elif query.data == "cari_lagi":
            # Clear previous data
            context.user_data.clear()
            
            # Send message asking for input
            query.message.edit_text(
                "🔍 *Cari Mahasiswa*\n\n"
                "Silakan masukkan nama lengkap atau NIM mahasiswa yang ingin dicari.\n\n"
                "📌 Contoh:\n"
                "• Ahmad Fauzi\n"
                "• 2020123456\n"
                "• Siti Nurhaliza\n"
                "• 2020987654",
                parse_mode='Markdown'
            )
            
            # Set flag to indicate we're waiting for search input
            context.user_data['waiting_for_search'] = True
            
    except Exception as e:
        logger.error(f"Error in button_callback: {str(e)}")
        query.message.edit_text(f"❌ Terjadi kesalahan: {str(e)}")

def register_user(update: Update, context: CallbackContext):
    """Handle /regist command"""
    try:
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Check if command is /regist ordalnant
        if not context.args or " ".join(context.args).lower() != "ordalnant":
            update.message.reply_text("❌ token registrasi salah")
            return
            
        # Load current allowed users
        allowed_users = load_allowed_users()
        
        # Check if user is already registered
        if any(user['id'] == user_id for user in allowed_users.get('users', [])):
            update.message.reply_text(
                "✅ Anda sudah terdaftar sebelumnya.\n"
                "Silakan gunakan bot dengan normal."
            )
            return
            
        # Add new user
        if not isinstance(allowed_users, dict):
            allowed_users = {"users": []}
        if "users" not in allowed_users:
            allowed_users["users"] = []
            
        allowed_users["users"].append({
            "id": user_id,
            "username": username,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Save updated allowed users
        with open(ALLOWED_USERS_FILE, 'w') as f:
            json.dump(allowed_users, f, indent=4)
            
        # Send success message
        update.message.reply_text(
            "✅ Registrasi berhasil!\n\n"
            "Sekarang Anda dapat menggunakan bot untuk mencari data mahasiswa.\n"
            "Gunakan command /cari diikuti nama atau NIM mahasiswa.\n\n"
            "Contoh:\n"
            "• /cari Ahmad Fauzi\n"
            "• /cari 2020123456"
        )
        
    except Exception as e:
        logger.error(f"Error in register_user: {str(e)}")
        update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

def main():
    """Start the bot"""
    try:
        print("\n=== Starting Student Search Bot ===")
        print(f"TELEGRAM_BOT_TOKEN: {TOKEN[:10]}...")
        print(f"ADMIN_BOT_TOKEN: {ADMIN_BOT_TOKEN[:10]}...")
        print(f"ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
        
        # Validate environment variables
        if not TOKEN:
            print("Error: TELEGRAM_BOT_TOKEN is empty")
            return
        if not ADMIN_BOT_TOKEN:
            print("Error: ADMIN_BOT_TOKEN is empty")
            return
        if not ADMIN_CHAT_ID:
            print("Error: ADMIN_CHAT_ID is empty")
            return
        
        # Create the Updater
        application = Updater(TOKEN)

        # Add handlers
        application.dispatcher.add_handler(CommandHandler("start", start))
        application.dispatcher.add_handler(CommandHandler("cari", search))
        application.dispatcher.add_handler(CommandHandler("regist", register_user))
        application.dispatcher.add_handler(CallbackQueryHandler(button_callback))
        
        # Add handlers for all types of messages
        application.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.photo, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.document, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.voice, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.video, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.sticker, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.location, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.contact, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.animation, handle_message))
        application.dispatcher.add_handler(MessageHandler(Filters.audio, handle_message))

        print("Handlers registered successfully")
        print("Starting polling...")

        # Start the bot
        application.start_polling()
        application.idle()
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        print(f"Error starting bot: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()