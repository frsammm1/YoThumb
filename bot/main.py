import os
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bot.handlers import start, help_command, status, cancel, genkey_command
from bot.handlers import handle_photo, handle_video, handle_text
from bot.database import Database
from bot.gdrive import GDrive
from bot.config import BOT_TOKEN, GDRIVE_ENABLED

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
gdrive = GDrive() if GDRIVE_ENABLED else None

async def keep_alive_task(application: Application):
    """Background task to keep bot active and clean up files"""
    counter = 0
    while True:
        try:
            await asyncio.sleep(1)
            counter += 1
            
            if counter % 600 == 0:
                logger.info(f"✅ Bot alive - {datetime.now()}")
                if gdrive:
                    logger.info("☁️ Google Drive: Connected")
            
            if counter % 3600 == 0:
                logger.info("🧹 Cleaning up old files...")
                await cleanup_old_files()
            
        except Exception as e:
            logger.error(f"Keep alive error: {e}")

async def cleanup_old_files():
    """Clean up temporary files older than 1 hour"""
    try:
        downloads_dir = "downloads"
        outputs_dir = "outputs"
        
        for directory in [downloads_dir, outputs_dir]:
            if os.path.exists(directory):
                now = datetime.now()
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if now - file_modified > timedelta(hours=1):
                            os.remove(filepath)
                            logger.info(f"Deleted old file: {filename}")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

async def main():
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("genkey", genkey_command))
    
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    asyncio.create_task(keep_alive_task(application))
    
    logger.info("🤖 Bot started successfully!")
    if gdrive:
        logger.info("☁️ Google Drive backup enabled")
    
    await application.run_polling(allowed_updates=Update.ALL_TYPES)
