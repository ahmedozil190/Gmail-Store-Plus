from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database import get_user, get_available_accounts_count, get_next_available_account, purchase_account, get_user_orders
from keyboards import get_main_keyboard, get_confirm_buy_keyboard
from strings import STRINGS
from config import DEFAULT_ACCOUNT_PRICE, ADMIN_ID
import logging

async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user: return
    
    lang = user['language']
    s = STRINGS[lang]
    
    count = get_available_accounts_count()
    if count == 0:
        await update.message.reply_text(s['SHOP_NO_ACCOUNTS'])
        return

    # Reset selection in user_data
    context.user_data['buy_qty'] = 1
    
    next_acc = get_next_available_account()
    price = next_acc['price'] if next_acc else DEFAULT_ACCOUNT_PRICE
    
    from keyboards import get_bulk_quantity_keyboard
    msg = s['SHOP_BULK_TITLE']
    
    # Bottom button for payment
    btn_key = 'BTN_PAY_TOTAL_1' if 1 == 1 else 'BTN_PAY_TOTAL_N'
    pay_btn_text = s[btn_key].format(price=price, qty=1, total=price)
    keyboard = list(get_bulk_quantity_keyboard(1).inline_keyboard)
    keyboard.append([InlineKeyboardButton(pay_btn_text, callback_data="confirm_bulk_buy")])
    
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def purchase_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    try:
        user = get_user(user_id)
        if not user: 
            await query.answer("User not found.")
            return
            
        lang = user['language']
        s = STRINGS[lang]
        
        if query.data.startswith("qty_"):
            await query.answer()
            qty = int(query.data.split("_")[1])
            context.user_data['buy_qty'] = qty
            
            # Update keyboard
            from keyboards import get_bulk_quantity_keyboard
            next_acc = get_next_available_account()
            price = next_acc['price'] if next_acc else DEFAULT_ACCOUNT_PRICE
            total_price = round(price * qty, 3)
            
            btn_key = 'BTN_PAY_TOTAL_1' if qty == 1 else 'BTN_PAY_TOTAL_N'
            pay_btn_text = s[btn_key].format(price=price, qty=qty, total=total_price)
            
            keyboard = list(get_bulk_quantity_keyboard(qty).inline_keyboard)
            keyboard.append([InlineKeyboardButton(pay_btn_text, callback_data="confirm_bulk_buy")])
            
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
            return

        if query.data == "cancel_buy":
            await query.answer()
            await query.message.delete()
            return

        if query.data == "confirm_bulk_buy":
            qty = context.user_data.get('buy_qty', 1)
            await query.answer(f"Processing purchase of {qty} accounts...")
            
            from database import purchase_bulk_accounts
            success, result = purchase_bulk_accounts(user_id, qty)
            
            if success:
                # result is a list of account objects
                msg = f"✅ <b>Purchase Successful!</b>\n\n"
                if lang == 'ar': msg = f"✅ <b>تمت عملية الشراء بنجاح!</b>\n\n"
                
                for acc in result:
                    msg += f"📧 <code>{acc['email']}:{acc['password']}</code>\n"
                
                if len(result) > 10:
                    msg = f"✅ <b>Purchase Successful! ({len(result)} accounts)</b>\n\nCheck your orders history / My Orders to see all account details."
                    if lang == 'ar': msg = f"✅ <b>تم شراء {len(result)} حساب بنجاح!</b>\n\nراجع 'طلباتي' لمشاهدة كافة التفاصيل."

                await query.message.edit_text(msg, parse_mode='HTML')
                
                # Notify Admin
                if ADMIN_ID:
                    try:
                        total_p = sum(a['price'] for a in result)
                        await context.bot.send_message(
                            ADMIN_ID,
                            f"🛍 <b>Bulk Buy</b>\nUser: {user['full_name']}\nQty: {qty}\nTotal: {total_p}$",
                            parse_mode='HTML'
                        )
                    except: pass
            else:
                await query.message.edit_text(f"❌ Error: {result}")
            return
            
    except Exception as e:
        import traceback
        logging.error(f"Error in purchase_callback: {e}\n{traceback.format_exc()}")
        await query.answer(f"❌ Error: {str(e)}", show_alert=True)

async def my_orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user: return
    
    lang = user['language']
    s = STRINGS[lang]
    
    orders = get_user_orders(user_id)
    if not orders:
        await update.message.reply_text(s['ORDERS_EMPTY'])
        return
        
    msg = s['ORDERS_TITLE'].format(count=len(orders))
    for o in orders[:10]: # Limit to last 10
        msg += s['ORDERS_ITEM'].format(
            email=o['email'],
            password=o['password'],
            date=o['purchased_at']
        )
        
    await update.message.reply_text(msg, parse_mode='HTML')
