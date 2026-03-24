from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from strings import STRINGS

def get_main_keyboard(lang):
    s = STRINGS[lang]
    keyboard = [
        [s['BTN_BUY']],
        [s['BTN_BALANCE'], s['BTN_DEPOSIT']],
        [InlineKeyboardButton("📱 Open App", web_app={"url": "https://gmail-store-plus-production.up.railway.app/"})],
        [s['BTN_MY_ORDERS'], s['BTN_HELP']],
        [s['BTN_SETTINGS']]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_settings_keyboard(lang):
    s = STRINGS[lang]
    keyboard = [
        [s['BTN_LANG']],
        [s['BTN_BACK']]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_languages_keyboard():
    keyboard = [
        [InlineKeyboardButton("العربية 🇪🇬", callback_data="lang_ar")],
        [InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_deposit_methods_keyboard(methods):
    keyboard = []
    for m in methods:
        keyboard.append([InlineKeyboardButton(m, callback_data=f"dep_method_{m}")])
    return InlineKeyboardMarkup(keyboard)

def get_confirm_buy_keyboard(lang):
    s = STRINGS[lang]
    keyboard = [
        [InlineKeyboardButton(s['BTN_CONFIRM_BUY'], callback_data="confirm_buy")],
        [InlineKeyboardButton(s['BTN_BACK'], callback_data="cancel_buy")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_bulk_quantity_keyboard(selected_qty=1):
    quantities = [1, 10, 50, 100, 200, 300, 500, 1000]
    keyboard = []
    
    for q in quantities:
        text = f"{'✓ ' if q == selected_qty else ''}{q} account{'s' if q > 1 else ''}{' ✓' if q == selected_qty else ''}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"qty_{q}")])
    
    return InlineKeyboardMarkup(keyboard)
