# database.py
import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name="smm_panel.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Users table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            balance REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            total_deposits REAL DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            referral_by INTEGER,
            banned INTEGER DEFAULT 0,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Settings table (for admin customization)
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        
        # Services table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            description TEXT,
            price REAL,
            min_quantity INTEGER,
            max_quantity INTEGER,
            status INTEGER DEFAULT 1
        )''')
        
        # Orders table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service_id INTEGER,
            link TEXT,
            quantity INTEGER,
            total_price REAL,
            status TEXT DEFAULT 'pending',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )''')
        
        # Deposits table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            transaction_id TEXT,
            status TEXT DEFAULT 'pending',
            deposit_date TIMESTAMP DEFAULT DEFAULT CURRENT_TIMESTAMP,
            approved_by INTEGER,
            approved_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )''')
        
        # Group join requirement
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS group_join (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            group_link TEXT,
            required INTEGER DEFAULT 1,
            check_message TEXT DEFAULT 'Join our group to use the bot'
        )''')
        
        # Broadcast logs
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS broadcast_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            message_type TEXT,
            users_count INTEGER,
            sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Initialize default settings
        self.init_default_settings()
        
        self.conn.commit()
    
    def init_default_settings(self):
        default_settings = {
            'welcome_message': '🚀 Welcome to SMM Panel Bot!\n\nUse the buttons below to navigate.',
            'bot_name': 'SMM Panel Bot',
            'support_username': '@SMMSupport',
            'invite_bonus': '10',
            'deposit_minimum': '50',
            'currency': '৳',
            'footer_text': '© 2024 SMM Panel Bot',
            'theme_emoji': '🎨',
            'button_balance': '💰 Balance',
            'button_services': '🛒 Get Service',
            'button_prices': '📊 Price & Info',
            'button_deposit': '💳 Deposit',
            'button_invite': '👥 Invite',
            'button_support': '🆘 Support',
            'button_stats': '📈 Statistics',
            'deposit_instructions': 'Send money to:\n📱 bKash: 01XXXXXXXXX\n📱 Nagad: 01XXXXXXXXX\n📱 Rocket: 01XXXXXXXXX\n\nAfter sending, submit transaction ID.',
            'payment_numbers': json.dumps({
                'bkash': '01XXXXXXXXX',
                'nagad': '01XXXXXXXXX',
                'rocket': '01XXXXXXXXX'
            }),
            'group_check': '1',
            'group_link': 'https://t.me/yourgroup',
            'group_message': '🔗 Join our group to use the bot:\n👉 https://t.me/yourgroup',
            'verify_button': '✅ I Have Joined'
        }
        
        for key, value in default_settings.items():
            self.cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
        
        self.conn.commit()
