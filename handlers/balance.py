from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from database import get_user, create_deposit_request
from keyboards import get_main_keyboard, get_deposit_methods_keyboard
from strings import STRINGS
from config import DEPOSIT_METHODS, DEPOSIT_INSTRUCTIONS, ADMIN_ID

# Conversation states
CHOOSING_METHOD, ENTERING_AMOUNT, ENTERING_SENDER_PHONE, SENDING_PROOF = range(4)

async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user: return
    
    lang = user['language']
    s = STRINGS[lang]
    
    msg = s['BALANCE_TITLE'] + s['BALANCE_INFO'].format(balance=user['balance'])
    await update.message.reply_text(msg, parse_mode='HTML')

async def start_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user: return
    
    lang = user['language']
    s = STRINGS[lang]
    
    await update.message.reply_text(
        s['DEPOSIT_TITLE'] + s['DEPOSIT_METHOD_PROMPT'],
        reply_markup=get_deposit_methods_keyboard(DEPOSIT_METHODS),
        parse_mode='HTML'
    )
    return CHOOSING_METHOD

async def method_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    method = query.data.replace("dep_method_", "")
    context.user_data['dep_method'] = method
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user['language']
    s = STRINGS[lang]
    
    await query.message.edit_text(
        s['DEPOSIT_AMOUNT_PROMPT'].format(method=method),
        parse_mode='HTML'
    )
    return ENTERING_AMOUNT

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount_str = update.message.text
    try:
        amount = float(amount_str)
        if amount <= 0: raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid positive number.")
        return ENTERING_AMOUNT
        
    context.user_data['dep_amount'] = amount
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user['language']
    s = STRINGS[lang]
    
    method = context.user_data['dep_method']
    
    if "Cryptomus" in method:
        from handlers.cryptomus import create_cryptomus_invoice
        from database import update_deposit_external_id
        
        # Create pending deposit in DB
        dep_id = create_deposit_request(user_id, amount, method, "Cryptomus Invoice")
        
        # Create Cryptomus Invoice
        url, uuid = await create_cryptomus_invoice(amount, str(dep_id))
        
        if url and uuid:
            update_deposit_external_id(dep_id, uuid)
            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = [[InlineKeyboardButton("💳 Pay Now / ادفع الآن", url=url)]]
            await update.message.reply_text(
                f"✅ <b>Cryptomus Invoice Created</b>\n\nAmount: <b>{amount}$</b>\n\nPlease click the button below to pay:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ Error creating invoice. Please try again or contact support.")
            return ConversationHandler.END
            
    instr = DEPOSIT_INSTRUCTIONS.get(method, "")
    
    if "Vodafone" in method:
        await update.message.reply_text(
            s['DEPOSIT_SENDER_PHONE_PROMPT'],
            parse_mode='HTML'
        )
        return ENTERING_SENDER_PHONE
    
    await update.message.reply_text(
        s['DEPOSIT_INSTRUCTIONS'].format(instructions=instr),
        parse_mode='HTML'
    )
    return SENDING_PROOF

async def sender_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    context.user_data['sender_phone'] = phone
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user['language']
    s = STRINGS[lang]
    
    method = context.user_data['dep_method']
    instr = DEPOSIT_INSTRUCTIONS.get(method, "")
    
    await update.message.reply_text(
        s['DEPOSIT_INSTRUCTIONS'].format(instructions=instr),
        parse_mode='HTML'
    )
    return SENDING_PROOF

async def proof_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proof = update.message.text or "Image/File" # In a real bot, we'd handle photos too
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user['language']
    s = STRINGS[lang]
    
    method = context.user_data['dep_method']
    amount = context.user_data['dep_amount']
    
    # Save to DB
    sender_phone = context.user_data.get('sender_phone', '')
    dep_id = create_deposit_request(user_id, amount, method, proof, sender_phone=sender_phone)
    
    # Notify User
    await update.message.reply_text(s['DEPOSIT_SUCCESS'], reply_markup=get_main_keyboard(lang))
    
    # Notify Admin
    if ADMIN_ID:
        try:
            await context.bot.send_message(
                ADMIN_ID,
                s['ADMIN_NOTIFY_DEPOSIT'].format(
                    user=f"{user['full_name']} ({user_id})",
                    amount=amount,
                    method=method,
                    sender_phone=sender_phone or "N/A",
                    proof=proof,
                    id=dep_id
                ),
                parse_mode='HTML'
            )
        except:
            pass
            
    return ConversationHandler.END

async def cancel_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = user['language']
    
    await update.message.reply_text(STRINGS[lang]['BTN_BACK'], reply_markup=get_main_keyboard(lang))
    return ConversationHandler.END

deposit_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(f"^({STRINGS['ar']['BTN_DEPOSIT']}|{STRINGS['en']['BTN_DEPOSIT']})$"), start_deposit)],
    states={
        CHOOSING_METHOD: [CallbackQueryHandler(method_callback, pattern="^dep_method_")],
        ENTERING_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)],
        ENTERING_SENDER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sender_phone_handler)],
        SENDING_PROOF:   [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, proof_handler)],
    },
    fallbacks=[MessageHandler(filters.Regex(f"^({STRINGS['ar']['BTN_BACK']}|{STRINGS['en']['BTN_BACK']})$"), cancel_deposit)],
)
