# admin_tools.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import json

class AdminTools:
    @staticmethod
    async def handle_admin_buttons(query, data, db):
        user_id = query.from_user.id
        
        if not db.is_admin(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        
        if data == 'admin_edit_welcome':
            await query.edit_message_text(
                "✏️ *Edit Welcome Message*\n\n"
                "Send the new welcome message:",
                parse_mode=ParseMode.MARKDOWN
            )
            # Store state for next message
            # Implementation depends on your state management
        
        elif data == 'admin_edit_buttons':
            await AdminTools.edit_buttons_menu(query, db)
        
        elif data == 'admin_edit_services':
            await AdminTools.edit_services_menu(query, db)
        
        elif data == 'admin_edit_deposit':
            await AdminTools.edit_deposit_menu(query, db)
        
        elif data == 'admin_group_settings':
            await AdminTools.group_settings_menu(query, db)
        
        elif data == 'admin_broadcast':
            await AdminTools.broadcast_menu(query, db)
        
        elif data == 'admin_user_control':
            await AdminTools.user_control_menu(query, db)
        
        elif data == 'admin_statistics':
            await AdminTools.show_admin_stats(query, db)
        
        elif data == 'admin_branding':
            await AdminTools.branding_menu(query, db)
    
    @staticmethod
    async def edit_buttons_menu(query, db):
        buttons = {
            'button_balance': db.get_setting('button_balance'),
            'button_services': db.get_setting('button_services'),
            'button_prices': db.get_setting('button_prices'),
            'button_deposit': db.get_setting('button_deposit'),
            'button_invite': db.get_setting('button_invite'),
            'button_support': db.get_setting('button_support'),
            'button_stats': db.get_setting('button_stats')
        }
        
        text = "⚙️ *Edit Menu Buttons*\n\n"
        for key, value in buttons.items():
            text += f"{key}: {value}\n"
        
        keyboard = []
        for key in buttons.keys():
            keyboard.append([
                InlineKeyboardButton(
                    f"Edit {key.split('_')[1].title()}",
                    callback_data=f"edit_button_{key}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='admin_panel')])
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def edit_deposit_menu(query, db):
        instructions = db.get_setting('deposit_instructions')
        payment_numbers = json.loads(db.get_setting('payment_numbers'))
        min_deposit = db.get_setting('deposit_minimum')
        
        text = "💳 *Deposit Settings*\n\n"
        text += f"Minimum Deposit: {min_deposit}৳\n\n"
        text += f"Instructions:\n{instructions}\n\n"
        text += "Payment Numbers:\n"
        for method, number in payment_numbers.items():
            text += f"{method}: {number}\n"
        
        keyboard = [
            [InlineKeyboardButton("Edit Instructions", callback_data='edit_deposit_instructions')],
            [InlineKeyboardButton("Edit Payment Numbers", callback_data='edit_payment_numbers')],
            [InlineKeyboardButton("Edit Minimum Deposit", callback_data='edit_min_deposit')],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_panel')]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def group_settings_menu(query, db):
        group_check = db.get_setting('group_check')
        group_link = db.get_setting('group_link')
        group_message = db.get_setting('group_message')
        verify_button = db.get_setting('verify_button')
        
        status = "✅ Enabled" if group_check == '1' else "❌ Disabled"
        
        text = "🔗 *Group Join Settings*\n\n"
        text += f"Status: {status}\n"
        text += f"Group Link: {group_link}\n"
        text += f"Message:\n{group_message}\n"
        text += f"Verify Button: {verify_button}"
        
        keyboard = [
            [InlineKeyboardButton(
                "Disable" if group_check == '1' else "Enable",
                callback_data='toggle_group_check'
            )],
            [InlineKeyboardButton("Edit Group Link", callback_data='edit_group_link')],
            [InlineKeyboardButton("Edit Message", callback_data='edit_group_message')],
            [InlineKeyboardButton("Edit Button Text", callback_data='edit_verify_button')],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_panel')]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def user_control_menu(query, db):
        text = "👤 *User Control*\n\n"
        text += "Search user by ID or username:"
        
        keyboard = [
            [InlineKeyboardButton("Ban User", callback_data='ban_user')],
            [InlineKeyboardButton("Unban User", callback_data='unban_user')],
            [InlineKeyboardButton("Add Balance", callback_data='add_balance')],
            [InlineKeyboardButton("Remove Balance", callback_data='remove_balance')],
            [InlineKeyboardButton("View User Info", callback_data='view_user')],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_panel')]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def branding_menu(query, db):
        bot_name = db.get_setting('bot_name')
        footer_text = db.get_setting('footer_text')
        theme_emoji = db.get_setting('theme_emoji')
        
        text = "🎨 *Branding Settings*\n\n"
        text += f"Bot Name: {bot_name}\n"
        text += f"Footer Text: {footer_text}\n"
        text += f"Theme Emoji: {theme_emoji}"
        
        keyboard = [
            [InlineKeyboardButton("Edit Bot Name", callback_data='edit_bot_name')],
            [InlineKeyboardButton("Edit Footer Text", callback_data='edit_footer')],
            [InlineKeyboardButton("Edit Theme Emoji", callback_data='edit_theme')],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_panel')]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def broadcast_menu(query, db):
        text = "📢 *Broadcast System*\n\n"
        text += "Send message to:\n\n"
        text += "1. All Users\n"
        text += "2. Active Users (last 7 days)\n"
        text += "3. Users with Deposits\n"
        text += "4. Forward Message"
        
        keyboard = [
            [InlineKeyboardButton("Broadcast to All", callback_data='broadcast_all')],
            [InlineKeyboardButton("Broadcast to Active", callback_data='broadcast_active')],
            [InlineKeyboardButton("Broadcast to Depositors", callback_data='broadcast_depositors')],
            [InlineKeyboardButton("Forward Message", callback_data='broadcast_forward')],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_panel')]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    @staticmethod
    async def handle_admin_message(update, context, db):
        # Handle admin text commands for editing settings
        # Implementation depends on state management
        pass
