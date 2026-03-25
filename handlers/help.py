from telegram import Update
from telegram.ext import ContextTypes
from database import get_user
from strings import STRINGS

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user: return
    
    lang = user['language']
    s = STRINGS[lang]
    
    msg = (
        "💬 Help & Tech Support\n\n"
        "To contact support: @A_M_E_15"
    )
    
    await update.message.reply_text(msg)
