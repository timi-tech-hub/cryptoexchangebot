import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # From @BotFather
ADMIN_IDS = [int(os.getenv("ADMIN_ID"))]  # Your Telegram user ID

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# TronGrid API (free)
TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY")
YOUR_USDT_WALLET = os.getenv("YOUR_USDT_WALLET", "TYourWalletAddressHere")  # Address where users send USDT

# Exchange rates (default, admin can change)
DEFAULT_BUY_RATE = 1480   # You buy USDT from user at ₦1480 per USDT
DEFAULT_SELL_RATE = 1520  # You sell USDT to user at ₦1520 per USDT

# Bank details for user deposits (displayed to users)
YOUR_BANK_NAME = "Moniepoint Microfinance Bank"
YOUR_BANK_ACCOUNT = "6541330333"
YOUR_BANK_ACCOUNT_NAME = "GraceApp Nigeria-mas"

# Optional: Real bank API (Paystack/Monnify) - leave empty for manual/admin confirmation
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "")
