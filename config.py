import os
from dotenv import load_dotenv

load_dotenv()

# ── Bot Credentials ──────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8687848556:AAHtl34uTW91j4SZeP-nGi-FH-yTinU7-ws")
_admin_id_raw = os.getenv("ADMIN_ID", "8741285999")
if _admin_id_raw.isdigit() or (_admin_id_raw.startswith("-") and _admin_id_raw[1:].isdigit()):
    ADMIN_ID = int(_admin_id_raw)
else:
    ADMIN_ID = 0

# ── Business Settings ────────────────────────────────────────────────────────
BOT_NAME = os.getenv("BOT_NAME", "Gmail Store Bot")
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "@A_M_E_15")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://gmail-store-plus-production.up.railway.app").rstrip("/")
VODAFONE_NUMBER = os.getenv("VODAFONE_NUMBER", "01140641198")
BASE_CURRENCY = "USD"

# ── Sale Settings ────────────────────────────────────────────────────────────
# Default price if not specified in the database for an account
DEFAULT_ACCOUNT_PRICE = float(os.getenv("DEFAULT_ACCOUNT_PRICE", "0.50"))

# ── Cryptomus Settings ───────────────────────────────────────────────────────
CRYPTOMUS_MERCHANT_ID = os.getenv("CRYPTOMUS_MERCHANT_ID", "Enter_In_DotEnv")
CRYPTOMUS_API_KEY     = os.getenv("CRYPTOMUS_API_KEY",     "Enter_In_DotEnv")
# The URL where the cryptomus callback will be sent (e.g., https://yourdomain.com/cryptomus_webhook)
CRYPTOMUS_CALLBACK_URL = os.getenv("CRYPTOMUS_CALLBACK_URL", "")

# ── Deposit Settings ─────────────────────────────────────────────────────────
DEPOSIT_METHODS = [
    "💳 Vodafone Cash",
    "🟡 Binance",
    "🟢 USDT (BEP20)",
    "💎 TRX (TRC20)",
    "🤖 Cryptomus (Crypto)",
]

# Instructions for each deposit method
DEPOSIT_INSTRUCTIONS = {
    "💳 Vodafone Cash": "أرسل المبلغ إلى الرقم: <code>01000000000</code>\nثم أرسل صورة التحويل أو رقمك المحول منه.",
    "🟡 Binance": "أرسل المبلغ إلى Binance ID: <code>12345678</code>\nثم أرسل صورة التحويل أو رقم المعاملة.",
    "🟢 USDT (BEP20)": "أرسل المبلغ إلى العنوان: <code>0x...</code>\nثم أرسل هاش المعاملة.",
    "💎 TRX (TRC20)": "أرسل المبلغ إلى العنوان: <code>T...</code>\nثم أرسل هاش المعاملة.",
    "🤖 Cryptomus (Crypto)": "سيتم توليد رابط دفع تلقائي لك. بمجرد الدفع سيتم تحديث الرصيد تلقائياً.",
}

# ── Dynamic Storage (Railway Volume Support) ──────────────────────────────────
# If /data exists (Railway Volume), use it. Otherwise use local directory.
DATA_DIR = "/data" if os.path.exists("/data") else os.path.dirname(os.path.abspath(__file__))
# Ensure common subdirectories exist in the data volume
os.makedirs(os.path.join(DATA_DIR, "uploads", "proofs"), exist_ok=True)

