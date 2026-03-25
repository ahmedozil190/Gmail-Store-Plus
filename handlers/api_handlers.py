from aiohttp import web
import json
from database import get_user, get_available_accounts_count, get_user_orders, get_next_available_account, get_admin_stats
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
async def get_admin_data(request):
    user_id = request.query.get('user_id')
    if not user_id or int(user_id) != ADMIN_ID:
        return web.json_response({'error': 'Unauthorized'}, status=403)
    
    stats = get_admin_stats()
    return web.json_response(stats)

def setup_api(app):
    app.router.add_get('/api/user_data', get_user_data)
    app.router.add_get('/api/shop_data', get_shop_data)
    app.router.add_get('/api/orders', get_orders)
    app.router.add_get('/api/admin_stats', get_admin_data)
