import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from config import BOT_TOKEN
from database import init_db
from handlers.start import start_handler, language_callback_handler
from handlers.settings import settings_handler, back_handler
from handlers.balance import balance_handler, deposit_conv_handler
from handlers.shop import shop_handler, purchase_callback_handler, my_orders_handler
from handlers.admin import admin_help_handler, add_accounts_handler, approve_dep_handler, reject_dep_handler
from handlers.webhook_handler import setup_webhook
from handlers.api_handlers import setup_api
from strings import STRINGS
from aiohttp import web
import os

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    # Initialise database
    init_db()
    logger.info("✅ Database initialised.")

    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handlers (should be before regular ones)
    app.add_handler(deposit_conv_handler)

    # Command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("admin", admin_help_handler))
    app.add_handler(CommandHandler("add_accounts", add_accounts_handler))
    app.add_handler(CommandHandler("approve_dep", approve_dep_handler))
    app.add_handler(CommandHandler("reject_dep", reject_dep_handler))

    # Text button handlers
    s_ar = STRINGS['ar']
    s_en = STRINGS['en']
    
    # Buy
    app.add_handler(MessageHandler(filters.Regex(f"^({s_ar['BTN_BUY']}|{s_en['BTN_BUY']})$"), shop_handler))
    # Balance
    app.add_handler(MessageHandler(filters.Regex(f"^({s_ar['BTN_BALANCE']}|{s_en['BTN_BALANCE']})$"), balance_handler))
    # My Orders
    app.add_handler(MessageHandler(filters.Regex(f"^({s_ar['BTN_MY_ORDERS']}|{s_en['BTN_MY_ORDERS']})$"), my_orders_handler))
    # Settings / Back
    app.add_handler(MessageHandler(filters.Regex(f"^({s_ar['BTN_SETTINGS']}|{s_en['BTN_SETTINGS']})$"), settings_handler))
    app.add_handler(MessageHandler(filters.Regex(f"^({s_ar['BTN_BACK']}|{s_en['BTN_BACK']})$"), back_handler))

    # Callbacks
    app.add_handler(CallbackQueryHandler(language_callback_handler, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(purchase_callback_handler, pattern="^(confirm_buy|cancel_buy|qty_.*|confirm_bulk_buy)$"))

    app.add_error_handler(error_handler)

    # ── Event Loop Setup (Fix for Python 3.14+) ──────────────────────────────
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    print("\n" + "="*40)
    print("🚀 GMAIL STORE BOT ACTIVE")
    print("="*40 + "\n")
    
    # ── Start Web Server (Webhooks + MiniApp) ──────────────────────────
    webhook_app = web.Application()
    setup_webhook(webhook_app, app)
    setup_api(webhook_app)

    # Static files
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_path): os.makedirs(static_path)
    webhook_app.router.add_static('/static/', static_path, name='static')
    
    async def serve_index(request): return web.FileResponse(os.path.join(static_path, 'index.html'))
    async def serve_admin(request): return web.FileResponse(os.path.join(static_path, 'admin.html'))
    
    webhook_app.router.add_get('/', serve_index)
    webhook_app.router.add_get('/admin_panel', serve_admin)

    # Start in the same event loop
    loop = asyncio.get_event_loop()
    runner = web.AppRunner(webhook_app)
    loop.run_until_complete(runner.setup())
    
    port = 8080 # Default port
    site = web.TCPSite(runner, '0.0.0.0', port)
    loop.run_until_complete(site.start())
    
    logger.info(f"🌐 Web server started on port {port}.")
    from config import CRYPTOMUS_CALLBACK_URL
    if CRYPTOMUS_CALLBACK_URL:
        logger.info(f"✅ Webhook active. Callback URL: {CRYPTOMUS_CALLBACK_URL}")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
