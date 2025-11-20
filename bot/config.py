import os
import json
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
SUPPORT_USERNAME = os.getenv('SUPPORT_USERNAME', 'YourUsername')

# Google Drive Configuration
GDRIVE_ENABLED = os.getenv('GDRIVE_ENABLED', 'false').lower() == 'true'
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')
GDRIVE_FOLDER_ID = os.getenv('GDRIVE_FOLDER_ID')

# Validate required variables
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")
if not OWNER_ID:
    raise ValueError("❌ OWNER_ID not found in environment variables!")

# Parse Google credentials if provided
GOOGLE_CREDENTIALS = None
if GOOGLE_CREDENTIALS_JSON and GDRIVE_ENABLED:
    try:
        GOOGLE_CREDENTIALS = json.loads(GOOGLE_CREDENTIALS_JSON)
    except json.JSONDecodeError:
        print("⚠️ Warning: Invalid GOOGLE_CREDENTIALS_JSON format")
        GDRIVE_ENABLED = False
