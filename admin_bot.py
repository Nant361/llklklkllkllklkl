import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Bot token
ADMIN_TOKEN = "7225070551:AAHOwwMUwQBZqYsKksd7HRjJEdt2kutjLp4"

# Admin user ID
ADMIN_ID = 5705926766

# File paths
ALLOWED_USERS_FILE = "allowed_users.json"
LOGS_FILE = "user_logs.json"

def load_allowed_users():
    """Load allowed users from JSON file"""
    if os.path.exists(ALLOWED_USERS_FILE):
        try:
            with open(ALLOWED_USERS_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and "users" in data:
                    return data
                elif isinstance(data, list):
                    return {"users": data}
                else:
                    print("Invalid data structure in allowed_users.json")
                    return {"users": []}
        except Exception as e:
            print(f"Error reading allowed_users.json: {str(e)}")
            return {"users": []}
    return {"users": []}

def save_allowed_users(users):
    """Save allowed users to JSON file"""
    with open(ALLOWED_USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_logs():
    """Load logs from JSON file"""
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_logs(logs):
    """Save logs to JSON file"""
    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

def log_activity(user_id, username, action, details=""):
    """Log user activity"""
    logs = load_logs()
    logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "username": username,
        "action": action,
        "details": details
    })
    save_logs(logs)

def start(update: Update, context: CallbackContext):
    """Handle /start command"""
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return
        
    update.message.reply_text(
        "👋 Welcome to Admin Bot\n\n"
        "🔑 Available Commands:\n"
        "-------------------\n"
        "📋 /list - View all allowed users\n"
        "➕ /add <user_id> <username> - Add new user\n"
        "❌ /remove <user_id> - Remove user access\n"
        "📊 /logs - View user activity logs\n"
        "🆔 /getid - Get user ID from forwarded message\n"
        "🆔 /chatid - Get the current chat ID\n\n"
        "💡 Tips:\n"
        "• Forward any message to get user ID\n"
        "• Use /getid command on forwarded message\n"
        "• Check logs regularly for monitoring\n\n"
        "👨‍💻 Developed by Nant\n"
        "✈️ Contact: @nant12_bot"
    )

def list_users(update: Update, context: CallbackContext):
    """Handle /list command"""
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return
        
    try:
        allowed_users = load_allowed_users()
        if not allowed_users.get('users'):
            update.message.reply_text("📝 Belum ada pengguna yang diizinkan.")
            return
            
        message = "📋 *Daftar Pengguna yang Diizinkan:*\n\n"
        for user in allowed_users['users']:
            message += f"• ID: `{user['id']}`\n"
            message += f"  Username: @{user.get('username', 'N/A')}\n"
            message += f"  Ditambahkan: {user.get('added_at', 'N/A')}\n\n"
            
        update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Error listing users: {str(e)}")
        update.message.reply_text("❌ Terjadi kesalahan saat mengambil daftar pengguna.")

def add_user(update: Update, context: CallbackContext):
    """Handle /add command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return
    
    if not context.args:
        update.message.reply_text("❌ Gunakan format: /add <user_id>")
        return
    
    try:
        new_user_id = int(context.args[0])
        allowed_users = load_allowed_users()
        
        # Ensure allowed_users has the correct structure
        if not isinstance(allowed_users, dict):
            allowed_users = {"users": []}
        if "users" not in allowed_users:
            allowed_users["users"] = []
        
        # Check if user already exists
        if any(user['id'] == new_user_id for user in allowed_users["users"]):
            update.message.reply_text("❌ Pengguna sudah terdaftar.")
            return
        
        # Add new user
        allowed_users["users"].append({
            "id": new_user_id,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_allowed_users(allowed_users)
        
        log_activity(user_id, username, "add_user", f"Added user ID: {new_user_id}")
        update.message.reply_text(f"✅ Pengguna dengan ID {new_user_id} berhasil ditambahkan.")
        
    except ValueError:
        update.message.reply_text("❌ ID pengguna harus berupa angka.")
    except Exception as e:
        print(f"Error adding user: {str(e)}")
        update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

def remove_user(update: Update, context: CallbackContext):
    """Handle /remove command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return
    
    if not context.args:
        update.message.reply_text("❌ Gunakan format: /remove <user_id>")
        return
    
    try:
        user_to_remove = int(context.args[0])
        allowed_users = load_allowed_users()
        
        # Ensure allowed_users has the correct structure
        if not isinstance(allowed_users, dict):
            allowed_users = {"users": []}
        if "users" not in allowed_users:
            allowed_users["users"] = []
        
        # Find and remove user
        allowed_users["users"] = [user for user in allowed_users["users"] if user['id'] != user_to_remove]
        save_allowed_users(allowed_users)
        
        log_activity(user_id, username, "remove_user", f"Removed user ID: {user_to_remove}")
        update.message.reply_text(f"✅ Pengguna dengan ID {user_to_remove} berhasil dihapus.")
        
    except ValueError:
        update.message.reply_text("❌ ID pengguna harus berupa angka.")
    except Exception as e:
        print(f"Error removing user: {str(e)}")
        update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")

def view_logs(update: Update, context: CallbackContext):
    """Handle /logs command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return
    
    logs = load_logs()
    if not logs:
        update.message.reply_text("📝 Belum ada log aktivitas.")
        return
    
    # Get last 10 logs
    recent_logs = logs[-10:]
    message = "📋 10 log aktivitas terakhir:\n\n"
    
    for log in recent_logs:
        message += f"Waktu: {log['timestamp']}\n"
        message += f"User ID: {log['user_id']}\n"
        message += f"Username: {log['username']}\n"
        message += f"Aksi: {log['action']}\n"
        if log['details']:
            message += f"Detail: {log['details']}\n"
        message += "-------------------\n"
    
    log_activity(user_id, username, "view_logs", "Viewed recent logs")
    update.message.reply_text(message)

def get_user_id(update: Update, context: CallbackContext):
    """Handle /getid command and forwarded messages"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    if user_id != ADMIN_ID:
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return
    
    message = update.message
    
    # Handle forwarded messages
    if message.forward_from_chat:
        user_info = f"Chat ID: {message.forward_from_chat.id}\n"
        user_info += f"Chat Type: {message.forward_from_chat.type}\n"
        user_info += f"Chat Title: {message.forward_from_chat.title}"
    elif message.forward_sender_name:
        user_info = f"Forwarded from: {message.forward_sender_name}"
    else:
        user_info = "Tidak dapat mendapatkan informasi pengirim"
    
    log_activity(user_id, username, "get_user_id", f"Got user info: {user_info}")
    message.reply_text(f"ℹ️ Informasi pengirim:\n\n{user_info}")

def get_chat_id(update: Update, context: CallbackContext):
    """Get the current chat ID"""
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ Maaf, Anda tidak memiliki akses ke bot ini.")
        return
        
    chat_id = update.effective_chat.id
    update.message.reply_text(f"Your chat ID is: `{chat_id}`", parse_mode='Markdown')

def main():
    """Start the bot"""
    try:
        # Create the Updater
        updater = Updater(ADMIN_TOKEN)

        # Add handlers
        updater.dispatcher.add_handler(CommandHandler("start", start))
        updater.dispatcher.add_handler(CommandHandler("list", list_users))
        updater.dispatcher.add_handler(CommandHandler("add", add_user))
        updater.dispatcher.add_handler(CommandHandler("remove", remove_user))
        updater.dispatcher.add_handler(CommandHandler("logs", view_logs))
        updater.dispatcher.add_handler(CommandHandler("getid", get_user_id))
        updater.dispatcher.add_handler(CommandHandler("chatid", get_chat_id))

        # Start the bot
        print("Starting Admin Bot...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(f"Error starting admin bot: {str(e)}")

if __name__ == "__main__":
    main() 