from telegram import Update
from telegram.ext import ContextTypes
from database import get_user
from keyboards import get_languages_keyboard, get_main_keyboard
from strings import STRINGS

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user: return
    
    lang = user['language']
    s = STRINGS[lang]
    
    await update.message.reply_text(s['BTN_SETTINGS'], reply_markup=get_main_keyboard(lang)) # For now just back or lang

async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user: return
    
    lang = user['language']
    s = STRINGS[lang]
    await update.message.reply_text(s['BTN_BACK'], reply_markup=get_main_keyboard(lang))
