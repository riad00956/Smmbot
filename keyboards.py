# keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu(db):
    # Get button texts from database
    buttons = {
        'balance': db.get_setting('button_balance'),
        'services': db.get_setting('button_services'),
        'prices': db.get_setting('button_prices'),
        'deposit': db.get_setting('button_deposit'),
        'invite': db.get_setting('button_invite'),
        'support': db.get_setting('button_support'),
        'stats': db.get_setting('button_stats')
    }
    
    keyboard = [
        [InlineKeyboardButton(buttons['balance'], callback_data='balance'),
         InlineKeyboardButton(buttons['services'], callback_data='services')],
        [InlineKeyboardButton(buttons['prices'], callback_data='prices'),
         InlineKeyboardButton(buttons['deposit'], callback_data='deposit')],
        [InlineKeyboardButton(buttons['invite'], callback_data='invite'),
         InlineKeyboardButton(buttons['support'], callback_data='support')],
        [InlineKeyboardButton(buttons['stats'], callback_data='stats')]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def back_to_main():
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='main_menu')]]
    return InlineKeyboardMarkup(keyboard)

def admin_panel():
    keyboard = [
        [InlineKeyboardButton("✏️ Edit Welcome Message", callback_data='admin_edit_welcome')],
        [InlineKeyboardButton("⚙️ Edit Menu Buttons", callback_data='admin_edit_buttons')],
        [InlineKeyboardButton("🛒 Edit Services", callback_data='admin_edit_services')],
        [InlineKeyboardButton("💳 Edit Deposit", callback_data='admin_edit_deposit')],
        [InlineKeyboardButton("🔗 Group Settings", callback_data='admin_group_settings')],
        [InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')],
        [InlineKeyboardButton("👤 User Control", callback_data='admin_user_control')],
        [InlineKeyboardButton("📊 Statistics", callback_data='admin_statistics')],
        [InlineKeyboardButton("🎨 Branding", callback_data='admin_branding')]
    ]
    return InlineKeyboardMarkup(keyboard)

def pagination_keyboard(items, page, total_pages, prefix):
    keyboard = []
    
    # Add items for current page
    for item in items:
        keyboard.append([InlineKeyboardButton(
            item['name'],
            callback_data=f"{prefix}_{item['id']}"
        )])
    
    # Add pagination buttons
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data='current_page'))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='admin_panel')])
    
    return InlineKeyboardMarkup(keyboard)
