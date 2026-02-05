# bot.py
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode
import database
import keyboards
import admin_tools
import services

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = database.Database()

# States for conversation
DEPOSIT_AMOUNT, DEPOSIT_TRX_ID, ORDER_LINK, ORDER_QUANTITY = range(4)

class SMMBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("admin", self.admin_panel))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Conversation handlers
        conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start_deposit, pattern='^deposit$'),
                CallbackQueryHandler(self.start_order, pattern='^service_')
            ],
            states={
                DEPOSIT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_deposit_amount)],
                DEPOSIT_TRX_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_deposit_trxid)],
                ORDER_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_order_link)],
                ORDER_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_order_quantity)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_conversation)]
        )
        self.application.add_handler(conv_handler)
        
        # Message handler for admin broadcast
        self.application.add_handler(MessageHandler(
            filters.TEXT & filters.ChatType.PRIVATE, 
            self.handle_message
        ))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Check if user is banned
        if db.is_user_banned(user.id):
            await update.message.reply_text("🚫 You are banned from using this bot.")
            return
        
        # Register user if not exists
        db.register_user(
            user.id,
            user.username,
            user.first_name,
            user.last_name
        )
        
        # Check group join requirement
        group_check = db.get_setting('group_check')
        if group_check == '1':
            group_link = db.get_setting('group_link')
            group_message = db.get_setting('group_message')
            verify_button = db.get_setting('verify_button')
            
            # Check if user is in group
            if not await self.check_group_membership(update, context, group_link):
                keyboard = [[InlineKeyboardButton(verify_button, callback_data='check_join')]]
                await update.message.reply_text(
                    group_message,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
        
        # Send welcome message
        welcome_msg = db.get_setting('welcome_message')
        bot_name = db.get_setting('bot_name')
        
        # Create main menu keyboard
        keyboard = keyboards.main_menu(db)
        
        await update.message.reply_text(
            f"👋 Welcome to *{bot_name}*\n\n{welcome_msg}",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def check_group_membership(self, update: Update, context: ContextTypes.DEFAULT_TYPE, group_link: str):
        # Extract group ID from link
        try:
            # This is a simplified check. In production, you'd use Telegram API to check membership
            # For now, we'll just check against a cached list
            user_id = update.effective_user.id
            # Implement actual group check here
            return True  # Placeholder
        except:
            return False
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        user_id = query.from_user.id
        
        # Check if user is banned
        if db.is_user_banned(user_id):
            await query.edit_message_text("🚫 You are banned from using this bot.")
            return
        
        # Handle different button clicks
        if data == 'balance':
            await self.show_balance(query)
        elif data == 'services':
            await self.show_services(query)
        elif data == 'prices':
            await self.show_prices(query)
        elif data == 'deposit':
            await self.start_deposit(update, context)
        elif data == 'invite':
            await self.show_invite(query)
        elif data == 'support':
            await self.show_support(query)
        elif data == 'stats':
            await self.show_statistics(query)
        elif data.startswith('category_'):
            await self.show_category_services(query, data.split('_')[1])
        elif data.startswith('service_'):
            await self.start_order(update, context)
        elif data == 'check_join':
            await self.verify_group_join(query, context)
        elif data == 'admin_edit_welcome':
            await self.admin_edit_welcome(query)
        elif data.startswith('admin_'):
            await admin_tools.handle_admin_buttons(query, data, db)
    
    async def show_balance(self, query):
        user_id = query.from_user.id
        balance = db.get_user_balance(user_id)
        currency = db.get_setting('currency')
        
        text = f"💰 *Your Balance*\n\n"
        text += f"Current Balance: *{balance} {currency}*\n"
        text += f"Total Orders: *{db.get_user_total_orders(user_id)}*\n"
        text += f"Total Deposits: *{db.get_user_total_deposits(user_id)} {currency}*\n"
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboards.back_to_main()
        )
    
    async def show_services(self, query):
        categories = db.get_service_categories()
        
        if not categories:
            await query.edit_message_text(
                "📭 No services available at the moment.",
                reply_markup=keyboards.back_to_main()
            )
            return
        
        text = "🛒 *Select Service Category*\n\n"
        keyboard = []
        
        for category in categories:
            keyboard.append([
                InlineKeyboardButton(
                    f"{category} Services",
                    callback_data=f"category_{category}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='main_menu')])
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_category_services(self, query, category):
        services_list = db.get_services_by_category(category)
        
        if not services_list:
            await query.edit_message_text(
                f"📭 No services available in {category} category.",
                reply_markup=keyboards.back_to_main()
            )
            return
        
        text = f"📦 *{category} Services*\n\n"
        keyboard = []
        
        for service in services_list:
            keyboard.append([
                InlineKeyboardButton(
                    f"{service['name']} - {service['price']}৳",
                    callback_data=f"service_{service['id']}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='services')])
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def start_deposit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if query:
            await query.edit_message_text(
                "💳 *Deposit Funds*\n\n"
                "Enter the amount you want to deposit:",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "💳 *Deposit Funds*\n\n"
                "Enter the amount you want to deposit:",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return DEPOSIT_AMOUNT
    
    async def get_deposit_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            amount = float(update.message.text)
            min_deposit = float(db.get_setting('deposit_minimum'))
            
            if amount < min_deposit:
                await update.message.reply_text(
                    f"❌ Minimum deposit amount is {min_deposit}৳\n"
                    f"Please enter a valid amount:"
                )
                return DEPOSIT_AMOUNT
            
            context.user_data['deposit_amount'] = amount
            
            # Show deposit instructions
            instructions = db.get_setting('deposit_instructions')
            
            await update.message.reply_text(
                f"📋 *Deposit Instructions*\n\n{instructions}\n\n"
                f"Amount: *{amount}৳*\n\n"
                "Please send the Transaction ID:",
                parse_mode=ParseMode.MARKDOWN
            )
            
            return DEPOSIT_TRX_ID
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter a valid number for the deposit amount:"
            )
            return DEPOSIT_AMOUNT
    
    async def get_deposit_trxid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        trx_id = update.message.text
        amount = context.user_data.get('deposit_amount')
        user_id = update.effective_user.id
        
        # Save deposit to database
        db.create_deposit(user_id, amount, trx_id)
        
        await update.message.reply_text(
            "✅ *Deposit Request Submitted!*\n\n"
            "Your deposit request has been sent for manual approval.\n"
            "You will be notified once approved.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboards.main_menu(db)
        )
        
        # Notify admin
        await self.notify_admin_deposit(user_id, amount, trx_id)
        
        return ConversationHandler.END
    
    async def start_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        service_id = int(query.data.split('_')[1])
        
        service = db.get_service(service_id)
        if not service:
            await query.edit_message_text("Service not found.")
            return
        
        context.user_data['order_service'] = service
        
        await query.edit_message_text(
            f"📝 *Order: {service['name']}*\n\n"
            f"Price: {service['price']}৳ per 1000\n"
            f"Min: {service['min_quantity']} | Max: {service['max_quantity']}\n\n"
            "Please send the link:",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ORDER_LINK
    
    async def get_order_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        link = update.message.text
        context.user_data['order_link'] = link
        
        await update.message.reply_text(
            "Now send the quantity:"
        )
        
        return ORDER_QUANTITY
    
    async def get_order_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            quantity = int(update.message.text)
            service = context.user_data.get('order_service')
            link = context.user_data.get('order_link')
            user_id = update.effective_user.id
            
            if quantity < service['min_quantity'] or quantity > service['max_quantity']:
                await update.message.reply_text(
                    f"Quantity must be between {service['min_quantity']} and {service['max_quantity']}"
                )
                return ORDER_QUANTITY
            
            # Calculate total price
            total_price = (service['price'] * quantity) / 1000
            
            # Check balance
            user_balance = db.get_user_balance(user_id)
            if user_balance < total_price:
                await update.message.reply_text(
                    f"❌ Insufficient balance!\n"
                    f"Required: {total_price}৳ | Available: {user_balance}৳",
                    reply_markup=keyboards.main_menu(db)
                )
                return ConversationHandler.END
            
            # Create order
            db.create_order(user_id, service['id'], link, quantity, total_price)
            
            # Deduct balance
            db.update_user_balance(user_id, -total_price)
            
            await update.message.reply_text(
                f"✅ *Order Placed Successfully!*\n\n"
                f"Service: {service['name']}\n"
                f"Link: {link}\n"
                f"Quantity: {quantity}\n"
                f"Total: {total_price}৳\n\n"
                f"Order ID: #{db.get_last_order_id()}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.main_menu(db)
            )
            
            # Notify admin
            await self.notify_admin_order(user_id, service['name'], quantity, total_price)
            
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text("Please enter a valid number for quantity:")
            return ORDER_QUANTITY
    
    async def show_invite(self, query):
        user_id = query.from_user.id
        invite_bonus = db.get_setting('invite_bonus')
        
        # Generate referral link
        bot_username = (await self.application.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={user_id}"
        
        text = f"👥 *Invite Friends & Earn*\n\n"
        text += f"Invite your friends and get *{invite_bonus}৳* for each referral!\n\n"
        text += f"Your referral link:\n`{referral_link}`\n\n"
        text += f"Total Referrals: *{db.get_user_referrals(user_id)}*\n"
        text += f"Earned from referrals: *{db.get_referral_earnings(user_id)}৳*"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_support(self, query):
        support_username = db.get_setting('support_username')
        
        text = "🆘 *Support*\n\n"
        text += f"Contact our support team: {support_username}\n\n"
        text += "We're here to help you 24/7!"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_statistics(self, query):
        stats = db.get_statistics()
        
        text = "📈 *Bot Statistics*\n\n"
        text += f"👥 Total Users: *{stats['total_users']}*\n"
        text += f"💰 Total Deposits: *{stats['total_deposits']}৳*\n"
        text += f"📦 Total Orders: *{stats['total_orders']}*\n"
        text += f"🆕 Today's Users: *{stats['today_users']}*\n"
        text += f"📊 Today's Orders: *{stats['today_orders']}*"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_menu')]]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        # Check if user is admin
        if not db.is_admin(user_id):
            await update.message.reply_text("❌ Access denied!")
            return
        
        keyboard = keyboards.admin_panel()
        
        await update.message.reply_text(
            "⚙️ *Admin Panel*\n\n"
            "Select an option to manage:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Handle admin commands and messages
        user_id = update.effective_user.id
        
        if db.is_admin(user_id):
            await admin_tools.handle_admin_message(update, context, db)
    
    async def cancel_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Operation cancelled.",
            reply_markup=keyboards.main_menu(db)
        )
        return ConversationHandler.END
    
    async def notify_admin_deposit(self, user_id, amount, trx_id):
        # Get all admins
        admins = db.get_admins()
        
        for admin_id in admins:
            try:
                await self.application.bot.send_message(
                    admin_id,
                    f"📥 *New Deposit Request*\n\n"
                    f"User: {user_id}\n"
                    f"Amount: {amount}৳\n"
                    f"TRX ID: {trx_id}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
    
    async def notify_admin_order(self, user_id, service_name, quantity, total_price):
        admins = db.get_admins()
        
        for admin_id in admins:
            try:
                await self.application.bot.send_message(
                    admin_id,
                    f"🛒 *New Order*\n\n"
                    f"User: {user_id}\n"
                    f"Service: {service_name}\n"
                    f"Quantity: {quantity}\n"
                    f"Total: {total_price}৳",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
