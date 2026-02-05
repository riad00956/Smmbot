# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Token from @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Admin User IDs (comma separated)
    ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
    
    # Database path
    DATABASE_PATH = os.getenv("DATABASE_PATH", "smm_panel.db")
    
    # Auto delete messages after seconds (0 to disable)
    AUTO_DELETE = int(os.getenv("AUTO_DELETE", "60"))
    
    # Anti-spam delay in seconds
    ANTI_SPAM_DELAY = int(os.getenv("ANTI_SPAM_DELAY", "2"))
