import os
import uuid
import secrets
import string
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import Database
from bot.video_processor import process_video_with_thumbnail
from bot.gdrive import GDrive
from bot.config import OWNER_ID, SUPPORT_USERNAME, GDRIVE_ENABLED

db = Database()
gdrive = GDrive() if GDRIVE_ENABLED else None
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    gdrive_status = "✅ Enabled" if GDRIVE_ENABLED else "❌ Disabled"
    
    welcome_text = f"""
🎬 **Welcome to Thumbnail Changer Bot!**

I can change thumbnails of your videos professionally.

**How to use:**
1️⃣ Get an auth key from admin
2️⃣ Send the key to activate
3️⃣ Send me a thumbnail image
4️⃣ Send me your video(s)
5️⃣ Receive videos with new thumbnails!

**Features:**
✅ High-quality video processing
✅ Preserve original quality
✅ Support all video formats
☁️ Google Drive Backup: {gdrive_status}

**Commands:**
/help - Show all commands
/status - Check subscription
/cancel - Cancel operation

Need a key? Contact: @{SUPPORT_USERNAME}
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
📚 **Bot Commands:**

/start - Start the bot
/help - Show this help
/status - Check subscription status
/cancel - Cancel current operation
/genkey <duration> - Generate auth key (admin only)

**Duration examples for /genkey:**
• 1h = 1 hour
• 1d = 1 day
• 7d = 7 days
• 30d = 30 days

**Supported Video Formats:**
• MP4, AVI, MKV, MOV, FLV, WMV

**Supported Image Formats:**
• JPG, JPEG, PNG, WEBP

**Support:** @{SUPPORT_USERNAME}
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscription = db.get_subscription(user_id)
    
    if not subscription:
        await update.message.reply_text("❌ No active subscription. Get an auth key to activate!")
        return
    
    expires_at = datetime.fromisoformat(subscription['expires_at'])
    now = datetime.now()
    
    if expires_at < now:
        await update.message.reply_text("⏰ Your subscription has expired. Get a new auth key!")
        return
    
    time_left = expires_at - now
    days_left = time_left.days
    hours_left = time_left.seconds // 3600
    
    status_text = f"""
✅ **Active Subscription**

⏰ Time remaining: {days_left} days, {hours_left} hours
📅 Expires: {expires_at.strftime('%Y-%m-%d %H:%M')}
📊 Videos processed: {subscription.get('videos_processed', 0)}
"""
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_states:
        if 'thumbnail' in user_states[user_id]:
            thumb_path = user_states[user_id]['thumbnail']
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        del user_states[user_id]
    await update.message.reply_text("✅ Operation cancelled.")

async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != int(OWNER_ID):
        await update.message.reply_text("❌ Only admin can generate keys!")
        return
    
    if not context.args:
        await update.message.reply_text("""
📝 **Generate Auth Key**

Usage: /genkey <duration>

Examples:
• /genkey 1d - 1 day subscription
• /genkey 7d - 7 days subscription
• /genkey 30d - 30 days subscription
• /genkey 1h - 1 hour subscription

Duration format: <number><unit>
Units: h (hours), d (days)
""", parse_mode='Markdown')
        return
    
    duration_str = context.args[0]
    duration = parse_duration(duration_str)
    
    if not duration:
        await update.message.reply_text("❌ Invalid duration format! Use: 1h, 1d, 7d, 30d")
        return
    
    auth_key = generate_auth_key()
    db.create_auth_key(auth_key, duration)
    
    key_text = f"""
🔑 **Auth Key Generated!**

Key: `{auth_key}`

⏰ Duration: {duration_str}
📋 Status: Active

**Instructions for user:**
1. Start the bot: @{context.bot.username}
2. Send this key: `{auth_key}`
3. Start using the bot!

Key expires after first use.
"""
    await update.message.reply_text(key_text, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if len(text) == 12 and text.isalnum() and text.isupper():
        key_data = db.verify_auth_key(text)
        if key_data:
            db.activate_subscription(user_id, key_data['duration_seconds'])
            duration_str = format_duration(key_data['duration_seconds'])
            await update.message.reply_text(
                f"✅ **Subscription Activated!**\n\n"
                f"⏰ Duration: {duration_str}\n"
                f"📅 Valid until: {(datetime.now() + timedelta(seconds=key_data['duration_seconds'])).strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Now send me a thumbnail image to start!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Invalid or expired auth key!")
        return
    
    await update.message.reply_text("ℹ️ Send /help to see available commands.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not db.has_active_subscription(user_id):
        await update.message.reply_text("❌ No active subscription! Get an auth key first.\n\nContact: @" + SUPPORT_USERNAME)
        return
    
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        
        thumb_path = f"downloads/thumb_{user_id}_{uuid.uuid4().hex[:8]}.jpg"
        await file.download_to_drive(thumb_path)
        
        if user_id in user_states and 'thumbnail' in user_states[user_id]:
            old_thumb = user_states[user_id]['thumbnail']
            if os.path.exists(old_thumb):
                os.remove(old_thumb)
        
        user_states[user_id] = {'thumbnail': thumb_path}
        
        await update.message.reply_text(
            "✅ Thumbnail saved!\n\n"
            "📹 Now send me your video(s).\n"
            "💡 You can send multiple videos with the same thumbnail."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error saving thumbnail: {str(e)}")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not db.has_active_subscription(user_id):
        await update.message.reply_text("❌ No active subscription! Get an auth key first.")
        return
    
    if user_id not in user_states or 'thumbnail' not in user_states[user_id]:
        await update.message.reply_text("⚠️ Send a thumbnail image first!")
        return
    
    status_msg = await update.message.reply_text("⏳ Processing video... Please wait.")
    
    video_path = None
    output_path = None
    
    try:
        video = update.message.video or update.message.document
        file = await context.bot.get_file(video.file_id)
        
        file_name = getattr(video, 'file_name', 'video.mp4')
        video_path = f"downloads/video_{user_id}_{uuid.uuid4().hex[:8]}_{file_name}"
        
        await status_msg.edit_text("📥 Downloading video...")
        await file.download_to_drive(video_path)
        
        await status_msg.edit_text("🎬 Changing thumbnail...")
        thumb_path = user_states[user_id]['thumbnail']
        output_path = await process_video_with_thumbnail(video_path, thumb_path)
        
        gdrive_link = None
        if gdrive:
            try:
                await status_msg.edit_text("☁️ Uploading to Google Drive...")
                gdrive_link = await gdrive.upload_file(output_path, f"processed_{file_name}")
            except Exception as e:
                print(f"GDrive upload error: {e}")
        
        await status_msg.edit_text("📤 Uploading processed video...")
        
        caption_text = "✅ Video with new thumbnail!"
        if gdrive_link:
            caption_text += f"\n\n☁️ [Download from Google Drive]({gdrive_link})"
        
        with open(output_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=caption_text,
                supports_streaming=True,
                parse_mode='Markdown'
            )
        
        await status_msg.delete()
        
        db.increment_videos_processed(user_id)
        
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error processing video: {str(e)}")
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)

def generate_auth_key(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def parse_duration(duration_str):
    try:
        if not duration_str or len(duration_str) < 2:
            return None
        value = int(duration_str[:-1])
        unit = duration_str[-1].lower()
        if unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        return None
    except:
        return None

def format_duration(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    if days > 0:
        return f"{days} day{'s' if days > 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        return f"{seconds // 60} minute{'s' if seconds > 60 else ''}"
