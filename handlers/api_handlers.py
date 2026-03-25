from aiohttp import web
import json
from database import get_user, get_available_accounts_count, get_user_orders

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
        'total_spent': total_spent
    })

async def get_orders(request):
    user_id = request.query.get('user_id')
    if not user_id:
        return web.json_response({'error': 'Missing user_id'}, status=400)
    
    orders = get_user_orders(int(user_id))
    return web.json_response([dict(o) for o in orders])

def setup_api(app):
    app.router.add_get('/api/user_data', get_user_data)
    app.router.add_get('/api/orders', get_orders)
