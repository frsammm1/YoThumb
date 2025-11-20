import os
import asyncio
import logging
from threading import Thread
from flask import Flask
from bot.main import main as bot_main

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Bot is running'}, 200

@app.route('/')
def home():
    return {'message': 'Thumbnail Changer Bot is Active'}, 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_bot():
    asyncio.run(bot_main())

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logging.info("🚀 Starting Thumbnail Changer Bot...")
    logging.info("🌐 Flask health server started")
    
    run_bot()
