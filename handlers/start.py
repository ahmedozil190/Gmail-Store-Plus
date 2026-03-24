from telegram import Update
from telegram.ext import ContextTypes
from database import get_user, create_user
from keyboards import get_main_keyboard, get_languages_keyboard
from strings import STRINGS

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    user = get_user(user_id)
    if not user:
        # First time user, ask for language
        await update.message.reply_text(
            "🌐 Choose Language / اختر اللغة:",
            reply_markup=get_languages_keyboard()
        )
        return

    lang = user['language']
    s = STRINGS[lang]

    await update.message.reply_text(s['START_MSG_1'])
    await update.message.reply_text(s['START_MSG_2'], reply_markup=get_main_keyboard(lang))

async def language_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split('_')[1]
    user_id = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    user = get_user(user_id)
    if not user:
        create_user(user_id, username, full_name, lang)
    else:
        from database import update_user_language
        update_user_language(user_id, lang)

    s = STRINGS[lang]
    await query.message.delete()
    await query.message.chat.send_message(
        s['START_MSG_1'],
        reply_markup=get_main_keyboard(lang)
    )
