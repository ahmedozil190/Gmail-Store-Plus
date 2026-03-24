from aiohttp import web
import json
from handlers.cryptomus import verify_cryptomus_signature
from database import get_deposit_by_external_id, approve_deposit, get_user
from strings import STRINGS

async def cryptomus_webhook(request):
    """
    Handles POST requests from Cryptomus.
    """
    try:
        data = await request.json()
        received_sign = data.get('sign')
        
        if not received_sign or not verify_cryptomus_signature(data, received_sign):
            return web.Response(text="Invalid signature", status=400)
        
        status = data.get('status')
        uuid = data.get('uuid')
        order_id = data.get('order_id') # This is our internal deposit ID
        
        if status in ['paid', 'paid_over']:
            # Find deposit
            dep = get_deposit_by_external_id(uuid)
            if not dep:
                # Try by order_id
                from database import _conn
                con = _conn()
                dep = con.execute("SELECT * FROM deposits WHERE id = ?", (order_id,)).fetchone()
                con.close()

            if dep and dep['status'] == 'pending':
                if approve_deposit(dep['id']):
                    # Notify User via Bot
                    # We'll need access to the bot instance
                    app = request.app.get('bot_app')
                    if app:
                        user = get_user(dep['user_id'])
                        lang = user['language'] if user else 'ar'
                        # Custom message for success
                        text = f"✅ <b>Payment Confirmed!</b>\n\nYour balance has been updated: <b>+{dep['amount']}$</b>"
                        if lang == 'ar':
                            text = f"✅ <b>تم تأكيد الدفع!</b>\n\nتم إضافة الرصيد لحسابك: <b>+{dep['amount']}$</b>"
                        
                        await app.bot.send_message(chat_id=dep['user_id'], text=text, parse_mode='HTML')
        
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"Webhook Error: {e}")
        return web.Response(text="Error", status=500)

def setup_webhook(app, bot_app):
    app['bot_app'] = bot_app
    app.router.add_post('/cryptomus_webhook', cryptomus_webhook)
