import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key, default=None, required=False):
    val = os.getenv(key, default)
    if required and not val:
        print(f"❌ ERROR: Missing required environment variable: {key}")
    return val

BOT_TOKEN = get_env("BOT_TOKEN", required=True)
ADMIN_ID_RAW = get_env("ADMIN_ID", required=True)
ADMIN_IDS = [int(ADMIN_ID_RAW)] if ADMIN_ID_RAW and ADMIN_ID_RAW.isdigit() else []

# Supabase
SUPABASE_URL = get_env("SUPABASE_URL", required=True)
SUPABASE_KEY = get_env("SUPABASE_KEY", required=True)

# TronGrid API
TRONGRID_API_KEY = get_env("TRONGRID_API_KEY")
YOUR_USDT_WALLET = get_env("YOUR_USDT_WALLET", "TYourWalletAddressHere")

# Bank details
YOUR_BANK_NAME = get_env("YOUR_BANK_NAME", "Moniepoint Microfinance Bank")
YOUR_BANK_ACCOUNT = get_env("YOUR_BANK_ACCOUNT", "6541330333")
YOUR_BANK_ACCOUNT_NAME = get_env("YOUR_BANK_ACCOUNT_NAME", "GraceApp Nigeria-mas")

DEFAULT_BUY_RATE = 1480
DEFAULT_SELL_RATE = 1520
PAYSTACK_SECRET_KEY = get_env("PAYSTACK_SECRET_KEY", "")
