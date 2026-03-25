from aiohttp import web
import json
from database import get_user, get_available_accounts_count, get_user_orders, get_next_available_account, get_admin_stats, get_all_users, get_all_accounts, get_all_deposits, approve_deposit, reject_deposit
from datetime import datetime
from config import DEFAULT_ACCOUNT_PRICE, ADMIN_ID

async def get_user_data(request):
    user_id = request.query.get('user_id')
    if not user_id:
        return web.json_response({'error': 'Missing user_id'}, status=400)
    
    user = get_user(int(user_id))
    if not user:
        return web.json_response({'error': 'User not found'}, status=404)
        
    orders = get_user_orders(int(user_id))
    total_spent = sum(o['price'] for o in orders)
    
    return web.json_response({
        'balance': user['balance'],
        'language': user['language'],
        'total_spent': total_spent,
        'total_accounts': len(orders)
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

async def get_orders(request):
    user_id = request.query.get('user_id')
    if not user_id:
        return web.json_response({'error': 'Missing user_id'}, status=400)
    
    orders = get_user_orders(int(user_id))
    return web.json_response(orders)

async def post_manual_deposit(request):
    try:
        reader = await request.multipart()
        
        data = {}
        file_path = None
        
        while True:
            part = await reader.next()
            if part is None:
                break
            
            if part.name == 'proof':
                filename = f"proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{part.filename}"
                file_path = f"static/uploads/proofs/{filename}"
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await part.read_chunk()
                        if not chunk:
                            break
                        f.write(chunk)
            else:
                data[part.name] = (await part.read()).decode('utf-8')

        user_id = data.get('user_id')
        amount = data.get('amount')
        
        if not user_id or not amount or not file_path:
            return web.json_response({'error': 'Missing required fields'}, status=400)

        from database import create_deposit_request
        # Method is 'Vodafone Cash'
        create_deposit_request(int(user_id), float(amount), 'Vodafone Cash', f"/{file_path}")
        
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
        
        if approve_deposit(int(dep_id)):
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
        
        reject_deposit(int(dep_id), reason)
        return web.json_response({'success': True})
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

def setup_api(app):
    app.router.add_get('/api/user_data', get_user_data)
    app.router.add_get('/api/shop_data', get_shop_data)
    app.router.add_get('/api/orders', get_orders)
    app.router.add_post('/api/manual_deposit', post_manual_deposit)
    app.router.add_get('/api/admin_stats', get_admin_data)
    app.router.add_get('/api/admin_users', get_admin_users)
    app.router.add_get('/api/admin_accounts', get_admin_accounts)
    app.router.add_get('/api/admin_deposits', get_admin_deposits)
    app.router.add_post('/api/approve_deposit', post_approve_deposit)
    app.router.add_post('/api/reject_deposit', post_reject_deposit)
