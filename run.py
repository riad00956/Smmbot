# run.py
import asyncio
from bot import SMMBot
from config import Config

def main():
    # Initialize bot
    bot = SMMBot(Config.BOT_TOKEN)
    
    print("🤖 SMM Panel Bot is starting...")
    print(f"👑 Admin IDs: {Config.ADMIN_IDS}")
    
    # Run bot
    bot.run()

if __name__ == "__main__":
    main()
