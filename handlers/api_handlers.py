from aiohttp import web
import json
import os
from database import get_user, get_available_accounts_count, get_user_orders, get_next_available_account, get_admin_stats, get_all_users, get_all_accounts, get_all_deposits, approve_deposit, reject_deposit
from datetime import datetime
import aiohttp
import asyncio
import hashlib
import base64
from config import DEFAULT_ACCOUNT_PRICE, ADMIN_ID, CRYPTOMUS_API_KEY, CRYPTOMUS_MERCHANT_ID, WEBAPP_URL, DATA_DIR

_rate_cache = {"rate": 52.7, "last_updated": 0}

async def get_live_rate():
    now = datetime.now().timestamp()
    # Cache for 1 hour
    if now - _rate_cache["last_updated"] < 3600:
        return _rate_cache["rate"]
    
    try:
        # 5 second timeout to prevent hanging the whole API
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://api.exchangerate-api.com/v4/latest/USD") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rate = data['rates'].get('EGP', _rate_cache["rate"])
                    _rate_cache["rate"] = rate
                    _rate_cache["last_updated"] = now
                    print(f"Live Rate Updated: {rate}")
                    return rate
                else:
                    print(f"Rate API returned status {resp.status}")
    except Exception as e:
        print(f"Rate Fetch Error: {e}")
    
    return _rate_cache["rate"]

async def get_user_data(request):
    user_id = request.query.get('user_id')
    if not user_id:
        return web.json_response({'error': 'Missing user_id'}, status=400)
    
    user = get_user(int(user_id))
    if not user:
        return web.json_response({'error': 'User not found'}, status=404)
        
    orders = get_user_orders(int(user_id))
    total_spent = sum(o['price'] for o in orders)
    
    from config import VODAFONE_NUMBER
    exchange_rate = await get_live_rate()
    return web.json_response({
        'balance': user['balance'],
        'language': user['language'],
        'total_spent': total_spent,
        'total_accounts': len(orders),
        'vodafone_number': VODAFONE_NUMBER,
        'exchange_rate': exchange_rate
    })

async def get_shop_data(request):
    try:
        count = get_available_accounts_count()
        next_acc = get_next_available_account()
        price = next_acc['price'] if next_acc else DEFAULT_ACCOUNT_PRICE
        
        # Log to console for debugging
        print(f"API Shop Request: Stock={count}, Price={price}")
        
        return web.json_response({
            'stock': count,
            'price': price,
            'product_name': 'High Quality Gmail Accounts',
            'product_desc': 'Available for immediate delivery.'
        })
    except Exception as e:
        print(f"API Shop Error: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def get_user_deposits_api(request):
    user_id = request.query.get('user_id')
    if not user_id:
        return web.json_response({'error': 'Missing user_id'}, status=400)
    
    from database import get_user_wallet_history
    history = get_user_wallet_history(int(user_id))
    return web.json_response(history)

async def get_orders(request):
    user_id = request.query.get('user_id')
    if not user_id:
        return web.json_response({'error': 'Missing user_id'}, status=400)
    
    orders = get_user_orders(int(user_id))
    return web.json_response(orders)

async def cryptomus_webhook(request):
    try:
        data = await request.post()
        if not data:
            data = await request.json()
            
        sign = data.get('sign')
        if not sign:
            return web.Response(text="No sign", status=400)

        # Verification logic: Cryptomus normally sends raw JSON + sign
        # But aiohttp request.json() might have already parsed it.
        # Simple check: the uuid should exist in our DB.
        uuid = data.get('uuid')
        status = data.get('status')
        
        if status in ['paid', 'partially_paid']:
            from database import get_deposit_by_external_id, approve_deposit
            dep = get_deposit_by_external_id(uuid)
            if dep and dep['status'] == 'pending':
                approve_deposit(dep['id'])
                print(f"Cryptomus Webhook: Deposit {dep['id']} approved automatically.")
        
        return web.Response(text="OK")
    except Exception as e:
        print(f"Webhook Error: {e}")
        return web.Response(text="Error", status=500)

async def post_create_crypto_invoice(request):
    try:
        data = await request.json()
        user_id = data.get('user_id')
        amount = data.get('amount')
        
        if not user_id or not amount:
            return web.json_response({'error': 'Missing data'}, status=400)

        # Cryptomus logic
        order_id = f"DEP_{int(datetime.now().timestamp())}_{user_id}"
        payload = {
            'amount': str(amount),
            'currency': 'USD',
            'order_id': order_id,
            'url_return': f"{WEBAPP_URL}/static/wallet.html",
            'url_callback': f"{WEBAPP_URL}/api/cryptomus_webhook",
            'is_sand_box': False
        }

        # Sign logic
        json_payload = json.dumps(payload)
        base64_payload = base64.b64encode(json_payload.encode()).decode()
        sign = hashlib.md5((base64_payload + CRYPTOMUS_API_KEY).encode()).hexdigest()

        headers = {
            'merchant': CRYPTOMUS_MERCHANT_ID,
            'sign': sign
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.cryptomus.com/v1/payment", json=payload, headers=headers) as resp:
                result = await resp.json()
                if resp.status == 200 and 'result' in result:
                    # Save pending deposit to DB
                    from database import create_deposit_request, update_deposit_external_id
                    dep_id = create_deposit_request(user_id, float(amount), 'Cryptomus', 'Pending Auto')
                    update_deposit_external_id(dep_id, result['result']['uuid'])
                    
                    return web.json_response({'url': result['result']['url']})
                else:
                    return web.json_response({'error': result.get('message', 'Cryptomus error')}, status=400)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def post_manual_deposit(request):
    try:
        reader = await request.multipart()
        data = {}
        file_content = None
        filename = None
        
        while True:
            part = await reader.next()
            if part is None: break
            
            if part.name == 'proof':
                filename = part.filename
                file_content = await part.read()
            else:
                data[part.name] = (await part.read()).decode('utf-8')

        user_id = data.get('user_id')
        amount = data.get('amount')
        sender_phone = data.get('sender_phone', '')
        
        if not user_id or not amount or not file_content:
            return web.json_response({'error': 'Missing required fields or file'}, status=400)

        # Save to Persistent Volume
        uploads_dir = os.path.join(DATA_DIR, 'static', 'uploads', 'proofs')
        os.makedirs(uploads_dir, exist_ok=True)
        
        ext = filename.split('.')[-1] if filename and '.' in filename else 'jpg'
        local_filename = f"proof_{user_id}_{int(datetime.now().timestamp())}.{ext}"
        abs_file_path = os.path.join(uploads_dir, local_filename)
        
        with open(abs_file_path, 'wb') as f:
            f.write(file_content)
        
        # The URL remains logical /static/uploads/...
        proof_url = f"/static/uploads/proofs/{local_filename}"

        # Calculate EGP amount
        rate = await get_live_rate()
        egp_amount = round(float(amount) * rate, 2)

        from database import create_deposit_request
        create_deposit_request(
            int(user_id), float(amount), 'Vodafone Cash', proof_url, 
            sender_phone=sender_phone, egp_amount=egp_amount, exchange_rate=rate
        )
        
        return web.json_response({'success': True})
    except Exception as e:
        print(f"Manual Deposit Error: {e}")
        return web.json_response({'error': str(e)}, status=500)
async def get_admin_data(request):
    try:
        user_id = request.query.get('user_id')
        if not user_id or not user_id.isdigit() or int(user_id) != ADMIN_ID:
            return web.json_response({'error': 'Unauthorized'}, status=403)
        stats = get_admin_stats()
        return web.json_response(stats)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def get_admin_users(request):
    try:
        user_id = request.query.get('user_id')
        if not user_id or not user_id.isdigit() or int(user_id) != ADMIN_ID:
            return web.json_response({'error': 'Unauthorized'}, status=403)
        return web.json_response(get_all_users())
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def get_admin_accounts(request):
    try:
        user_id = request.query.get('user_id')
        if not user_id or not user_id.isdigit() or int(user_id) != ADMIN_ID:
            return web.json_response({'error': 'Unauthorized'}, status=403)
        return web.json_response(get_all_accounts())
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def get_admin_deposits(request):
    try:
        user_id = request.query.get('user_id')
        if not user_id or not user_id.isdigit() or int(user_id) != ADMIN_ID:
            return web.json_response({'error': 'Unauthorized'}, status=403)
        return web.json_response(get_all_deposits())
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def post_approve_deposit(request):
    try:
        data = await request.json()
        user_id = data.get('admin_id')
        dep_id = data.get('dep_id')
        if not user_id or str(user_id) != str(ADMIN_ID):
            return web.json_response({'error': 'Unauthorized'}, status=403)
        
        dep = approve_deposit(int(dep_id))
        if dep:
            # Notify user
            bot = request.app['bot_app'].bot
            from strings import STRINGS
            from database import get_user
            u = get_user(dep['user_id'])
            lang = u['language'] if u else 'ar'
            msg = STRINGS[lang]['DEPOSIT_APPROVED_NOTIFY'].format(amount=dep['amount'])
            try:
                await bot.send_message(chat_id=dep['user_id'], text=msg, parse_mode='HTML')
            except Exception as e:
                print(f"Error sending approval notification: {e}")

            return web.json_response({'success': True})
        return web.json_response({'error': 'Failed to approve'}, status=400)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def post_reject_deposit(request):
    try:
        data = await request.json()
        user_id = data.get('admin_id')
        dep_id = data.get('dep_id')
        reason = data.get('reason', 'Rejected by admin')
        if not user_id or str(user_id) != str(ADMIN_ID):
            return web.json_response({'error': 'Unauthorized'}, status=403)
        
        dep = reject_deposit(int(dep_id), reason)
        if dep:
            # Notify user
            bot = request.app['bot_app'].bot
            from strings import STRINGS
            from database import get_user
            u = get_user(dep['user_id'])
            lang = u['language'] if u else 'ar'
            msg = STRINGS[lang]['DEPOSIT_REJECTED_NOTIFY'].format(amount=dep['amount'], reason=reason)
            try:
                await bot.send_message(chat_id=dep['user_id'], text=msg, parse_mode='HTML')
            except Exception as e:
                print(f"Error sending rejection notification: {e}")

            return web.json_response({'success': True})
        return web.json_response({'success': True})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

def setup_api(app, bot_app):
    app['bot_app'] = bot_app
    app.router.add_get('/api/user_data', get_user_data)
    app.router.add_get('/api/shop_data', get_shop_data)
    app.router.add_get('/api/orders', get_orders)
    app.router.add_get('/api/user_deposits', get_user_deposits_api)
    app.router.add_post('/api/manual_deposit', post_manual_deposit)
    app.router.add_post('/api/create_crypto_invoice', post_create_crypto_invoice)
    app.router.add_post('/api/cryptomus_webhook', cryptomus_webhook)
    app.router.add_get('/api/admin_stats', get_admin_data)
    app.router.add_get('/api/admin_users', get_admin_users)
    app.router.add_get('/api/admin_accounts', get_admin_accounts)
    app.router.add_get('/api/admin_deposits', get_admin_deposits)
    app.router.add_post('/api/approve_deposit', post_approve_deposit)
    app.router.add_post('/api/reject_deposit', post_reject_deposit)
