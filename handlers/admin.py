from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler
from database import add_account_to_pool, approve_deposit, reject_deposit, get_user, get_admin_stats
from config import ADMIN_ID, DEFAULT_ACCOUNT_PRICE, WEBAPP_URL
from strings import STRINGS

async def admin_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    user = get_user(update.effective_user.id)
    lang = user['language'] if user else 'ar'
    s = STRINGS[lang]
    
    await update.message.reply_text(s['ADMIN_HELP'], parse_mode='HTML')

async def add_accounts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    # Usage: /add_accounts email:pass [email:pass ...]
    if not context.args:
        await update.message.reply_text("Usage: /add_accounts email:pass [email:pass ...]")
        return
        
    added = 0
    for entry in context.args:
        if ":" in entry:
            email, pwd = entry.split(":", 1)
            if add_account_to_pool(email.strip(), pwd.strip(), price=DEFAULT_ACCOUNT_PRICE):
                added += 1
                
    await update.message.reply_text(f"✅ Added {added} accounts to the pool.")

async def approve_dep_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    if not context.args: return
    dep_id = int(context.args[0])
    
    if approve_deposit(dep_id):
        await update.message.reply_text(f"✅ Deposit #{dep_id} approved.")
        # We should notify the user here too, but for simplicity we skip for now
    else:
        await update.message.reply_text(f"❌ Could not approve deposit #{dep_id}.")

async def reject_dep_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    if not context.args: return
    dep_id = int(context.args[0])
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Unknown"
    
    reject_deposit(dep_id, reason)
    await update.message.reply_text(f"🚫 Deposit #{dep_id} rejected. Reason: {reason}")

async def admin_dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    user = get_user(update.effective_user.id)
    lang = user['language'] if user else 'ar'
    s = STRINGS[lang]
    
    stats = get_admin_stats()
    text = s['ADMIN_DASHBOARD_STATS'].format(**stats)
    text += f"\n\n🔗 <b>Direct Link:</b> {WEBAPP_URL}/static/admin.html"
    text += f"\n\n⚙️ <i>If the button below (Not Found), please check your WEBAPP_URL in Railway.</i>"
    
    keyboard = [
        [InlineKeyboardButton(s['BTN_ADMIN_PANEL'], web_app=WebAppInfo(url=f"{WEBAPP_URL}/static/admin.html"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
