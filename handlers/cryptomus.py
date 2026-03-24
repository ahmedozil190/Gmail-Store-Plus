import hashlib
import json
import aiohttp
from config import CRYPTOMUS_MERCHANT_ID, CRYPTOMUS_API_KEY, CRYPTOMUS_CALLBACK_URL

async def create_cryptomus_invoice(amount: float, order_id: str):
    """
    Creates a Cryptomus invoice and returns the payment URL.
    """
    url = "https://api.cryptomus.com/v1/payment"
    
    payload = {
        "amount": str(amount),
        "currency": "USD",
        "order_id": str(order_id),
        "url_callback": CRYPTOMUS_CALLBACK_URL,
        # "url_success": "https://t.me/your_bot_username", # Optional
    }
    
    # Generate signature: base64(payload) + API_KEY -> MD5 (Wait, Cryptomus uses a different sign logic)
    # Correct logic for v1: md5(base64_encode(json_payload) + API_KEY)
    import base64
    
    payload_json = json.dumps(payload)
    sign_source = base64.b64encode(payload_json.encode()).decode() + CRYPTOMUS_API_KEY
    sign = hashlib.md5(sign_source.encode()).hexdigest()
    
    headers = {
        "merchant": CRYPTOMUS_MERCHANT_ID,
        "sign": sign,
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            if resp.status == 200 and data.get('result'):
                # Return the payment URL and the Cryptomus UUID
                return data['result']['url'], data['result']['uuid']
            else:
                print(f"Cryptomus Error: {data}")
                return None, None

def verify_cryptomus_signature(payload_dict, received_sign):
    """
    Verifies the signature from Cryptomus callback.
    """
    # Exclude 'sign' from payload
    data = payload_dict.copy()
    if 'sign' in data:
        del data['sign']
        
    import base64
    payload_json = json.dumps(data)
    sign_source = base64.b64encode(payload_json.encode()).decode() + CRYPTOMUS_API_KEY
    expected_sign = hashlib.md5(sign_source.encode()).hexdigest()
    
    return expected_sign == received_sign
