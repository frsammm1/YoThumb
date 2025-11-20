# 🎬 Thumbnail Changer Bot

Professional Telegram bot for changing video thumbnails with subscription management and Google Drive backup.

## ✨ Features

- Change video thumbnails instantly
- Preserve original video quality
- Google Drive backup integration
- Subscription system with auth keys
- 24/7 uptime on free hosting
- Auto file cleanup

## 🚀 Quick Setup

### 1. Get Bot Credentials

**Bot Token:**
- Go to [@BotFather](https://t.me/BotFather)
- Send `/newbot` and follow instructions
- Copy token: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

**Your User ID:**
- Go to [@userinfobot](https://t.me/userinfobot)
- Copy your ID: `123456789`

### 2. Google Drive Setup (Optional)

1. Create project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Drive API
3. Create Service Account → Generate JSON key
4. Create folder in Google Drive
5. Share folder with service account email (from JSON)
6. Copy folder ID from URL
7. Convert JSON to single line (no line breaks!)

### 3. Deploy on Render

**Push to GitHub:**
```bash
chmod +x *.sh
./1_create_requirements.sh
./2_create_render_yaml.sh
./3_create_run_py.sh
./4_create_bot_main.sh
./5_create_bot_handlers.sh
./6_create_bot_modules.sh
./7_create_config_files.sh
./8_create_readme.sh
```

**Deploy:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. New + → Web Service → Connect GitHub repo
3. Configure:
   - Name: `newthumbchangingbot247`
   - Build: `pip install -r requirements.txt`
   - Start: `python run.py`

**Environment Variables:**
```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OWNER_ID=123456789
SUPPORT_USERNAME=yourusername
GDRIVE_ENABLED=true
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
GDRIVE_FOLDER_ID=1a2b3c4d5e6f7g8h9i0j
```

## 📝 Commands

**Admin:**
- `/genkey 7d` - Generate 7-day subscription key
- `/genkey 30d` - Generate 30-day key
- `/genkey 1h` - Generate 1-hour key

**Users:**
- `/start` - Start bot
- `/help` - Show help
- `/status` - Check subscription
- `/cancel` - Cancel operation

## 🎮 How to Use

**For Users:**
1. Send auth key to bot (e.g., `A1B2C3D4E5F6`)
2. Send thumbnail image
3. Send video file(s)
4. Receive processed video!

## 🐛 Troubleshooting

**Bot not responding?**
- Check Render logs for errors
- Verify BOT_TOKEN is correct
- Restart service on Render

**Google Drive not working?**
- Verify JSON is single line
- Check service account has Editor access
- Ensure GDRIVE_ENABLED=true

**Video processing fails?**
- Check video size (free tier limits)
- Verify supported format (MP4, AVI, MKV, MOV)

**Auth keys not working?**
- Verify OWNER_ID matches your Telegram ID
- Check key format (12 uppercase alphanumeric)

## 📂 File Structure

```
NewThumbChangingBot247/
├── bot/
│   ├── main.py              # Bot core
│   ├── handlers.py          # Commands
│   ├── database.py          # Data storage
│   ├── video_processor.py   # FFmpeg processing
│   ├── gdrive.py           # Google Drive
│   └── config.py           # Configuration
├── run.py                  # Entry point
├── requirements.txt        # Dependencies
└── render.yaml            # Deploy config
```

## 📞 Support

- GitHub Issues: [Create Issue](https://github.com/yourusername/NewThumbChangingBot247/issues)
- Telegram: @YourUsername

## 📄 License

MIT License - Free to use and modify

---

Made with ❤️ for video editing enthusiasts
