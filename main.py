import logging
import signal
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
import admin_bot
import telegram_bot

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global updaters for signal handling
admin_updater = None
student_updater = None

def run_admin_bot():
    """Run the admin bot"""
    global admin_updater
    try:
        logger.info("Starting Admin Bot...")
        admin_updater = Updater(admin_bot.ADMIN_TOKEN)
        dispatcher = admin_updater.dispatcher

        # Add handlers
        dispatcher.add_handler(CommandHandler("start", admin_bot.start))
        dispatcher.add_handler(CommandHandler("list", admin_bot.list_users))
        dispatcher.add_handler(CommandHandler("add", admin_bot.add_user))
        dispatcher.add_handler(CommandHandler("remove", admin_bot.remove_user))
        dispatcher.add_handler(CommandHandler("logs", admin_bot.view_logs))
        dispatcher.add_handler(CommandHandler("getid", admin_bot.get_user_id))
        dispatcher.add_handler(CommandHandler("chatid", admin_bot.get_chat_id))
        dispatcher.add_handler(MessageHandler(Filters.forwarded, admin_bot.get_user_id))

        logger.info("Admin Bot is ready!")
        # Start the Bot
        admin_updater.start_polling()
            
    except Exception as e:
        logger.error(f"Error in Admin Bot: {str(e)}", exc_info=True)
        if admin_updater:
            admin_updater.stop()
        return False
    
    return True

def run_student_bot():
    """Run the student search bot"""
    global student_updater
    try:
        logger.info("Starting Student Search Bot...")
        student_updater = Updater(telegram_bot.TOKEN)
        dispatcher = student_updater.dispatcher

        # Add handlers
        dispatcher.add_handler(CommandHandler("start", telegram_bot.start))
        dispatcher.add_handler(CommandHandler("cari", telegram_bot.search))
        dispatcher.add_handler(CommandHandler("regist", telegram_bot.register_user))
        dispatcher.add_handler(CallbackQueryHandler(telegram_bot.button_callback))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.photo, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.document, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.voice, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.video, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.sticker, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.location, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.contact, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.animation, telegram_bot.handle_message))
        dispatcher.add_handler(MessageHandler(Filters.audio, telegram_bot.handle_message))

        logger.info("Student Search Bot is ready!")
        # Start the Bot
        student_updater.start_polling()
            
    except Exception as e:
        logger.error(f"Error in Student Search Bot: {str(e)}", exc_info=True)
        if student_updater:
            student_updater.stop()
        return False
    
    return True

def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info("Received termination signal. Shutting down bots...")
    if admin_updater:
        admin_updater.stop()
    if student_updater:
        student_updater.stop()
    sys.exit(0)

def main():
    """Run both bots"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Starting both bots...")
        
        # Start both bots
        admin_success = run_admin_bot()
        student_success = run_student_bot()
        
        if not admin_success or not student_success:
            logger.error("Failed to start one or both bots. Exiting...")
            if admin_updater:
                admin_updater.stop()
            if student_updater:
                student_updater.stop()
            return

        # Keep the program running
        admin_updater.idle()
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}", exc_info=True)
        if admin_updater:
            admin_updater.stop()
        if student_updater:
            student_updater.stop()
        sys.exit(1)

if __name__ == "__main__":
    main() 