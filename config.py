"""
Configuration module for the Nigerian P2P Crypto Exchange Bot.
Handles environment variable loading and provides a centralized settings interface.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Safely retrieve an environment variable.
    
    Args:
        key: The environment variable key.
        default: The default value if the key is not found.
        required: If True, prints an error message if the key is missing.
        
    Returns:
        The value of the environment variable or the default.
    """
    val = os.getenv(key, default)
    if required and not val:
        # Using print here as logging might not be initialized yet in all entry points
        print(f"❌ CRITICAL CONFIG ERROR: Missing required environment variable: {key}")
    return val or ""

# --- Telegram Configuration ---
BOT_TOKEN: str = get_env("BOT_TOKEN", required=True)
ADMIN_ID_RAW: str = get_env("ADMIN_ID", required=True)
ADMIN_IDS: List[int] = [int(ADMIN_ID_RAW)] if ADMIN_ID_RAW and ADMIN_ID_RAW.isdigit() else []

# --- Supabase Configuration (Database) ---
SUPABASE_URL: str = get_env("SUPABASE_URL", required=True)
SUPABASE_KEY: str = get_env("SUPABASE_KEY", required=True)

# --- Tron/Blockchain Configuration ---
TRONGRID_API_KEY: str = get_env("TRONGRID_API_KEY")
YOUR_USDT_WALLET: str = get_env("YOUR_USDT_WALLET", "TYourWalletAddressHere")

# --- Merchant Bank Details ---
YOUR_BANK_NAME: str = get_env("YOUR_BANK_NAME", "Moniepoint Microfinance Bank")
YOUR_BANK_ACCOUNT: str = get_env("YOUR_BANK_ACCOUNT", "6541330333")
YOUR_BANK_ACCOUNT_NAME: str = get_env("YOUR_BANK_ACCOUNT_NAME", "GraceApp Nigeria-mas")

# --- Trading Parameters ---
DEFAULT_BUY_RATE: int = 1480  # Default if not set in DB
DEFAULT_SELL_RATE: int = 1520 # Default if not set in DB

# --- Optional Integrations ---
PAYSTACK_SECRET_KEY: str = get_env("PAYSTACK_SECRET_KEY", "")

