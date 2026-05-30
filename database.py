"""
Database management module for the Nigerian P2P Crypto Exchange Bot.
Interfaces with Supabase (PostgreSQL) for persistent data storage.
"""

import logging
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Setup logging for database operations
logger = logging.getLogger(__name__)

# Initialize Supabase client
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.critical("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    raise ValueError("Missing database credentials.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db() -> None:
    """
    Ensures the remote database is ready.
    Sets default system-wide parameters if they are missing.
    """
    logger.info("Initializing system settings...")
    set_setting_if_not_exists('buy_rate', '1480')
    set_setting_if_not_exists('sell_rate', '1520')

def set_setting_if_not_exists(key: str, value: str) -> None:
    """
    Sets a default setting if no value currently exists for the given key.
    
    Args:
        key: The setting identifier.
        value: The default value to assign.
    """
    existing = get_setting(key)
    if existing is None:
        set_setting(key, value)

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves a user's profile from the database.
    
    Args:
        user_id: The Telegram user ID.
        
    Returns:
        A dictionary containing user data or None if not found.
    """
    try:
        response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
    return None

def register_user(user_id: int, phone: str, bank_name: str, bank_account_name: str, 
                  bank_account_number: str, crypto_address: str) -> None:
    """
    Registers a new user or updates an existing user profile using an UPSERT operation.
    
    Args:
        user_id: The Telegram user ID.
        phone: User's contact number.
        bank_name: Name of the user's bank.
        bank_account_name: Name on the bank account.
        bank_account_number: 10-digit account number.
        crypto_address: USDT (TRC20) wallet address.
    """
    data = {
        'user_id': user_id,
        'phone': phone,
        'bank_name': bank_name,
        'bank_account_name': bank_account_name,
        'bank_account_number': bank_account_number,
        'crypto_address': crypto_address
    }
    try:
        supabase.table('users').upsert(data).execute()
    except Exception as e:
        logger.error(f"Error upserting user {user_id}: {e}")

def auto_create_user(user_id: int) -> Dict[str, Any]:
    """
    Ensures a user exists in the database. Creates a blank profile if not present.
    
    Args:
        user_id: The Telegram user ID.
        
    Returns:
        The user's profile data dictionary.
    """
    user = get_user(user_id)
    if not user:
        logger.info(f"Creating new profile for user {user_id}")
        register_user(user_id, "", "", "", "", "")
        user = get_user(user_id)
    return user or {}

def update_balance(user_id: int, naira_delta: float = 0.0, usdt_delta: float = 0.0) -> None:
    """
    Updates a user's internal balances. (Mainly for compatibility with legacy flows).
    
    Args:
        user_id: The Telegram user ID.
        naira_delta: Amount to add/subtract from Naira balance.
        usdt_delta: Amount to add/subtract from USDT balance.
    """
    user = get_user(user_id)
    if not user:
        return
    
    new_naira = (user.get('naira_balance') or 0) + naira_delta
    new_usdt = (user.get('usdt_balance') or 0) + usdt_delta
    
    try:
        supabase.table('users').update({
            'naira_balance': new_naira,
            'usdt_balance': new_usdt
        }).eq('user_id', user_id).execute()
    except Exception as e:
        logger.error(f"Error updating balance for {user_id}: {e}")

def add_transaction(user_id: int, tx_type: str, amount_currency: str, amount: float, 
                    rate: float, status: str, tx_hash: Optional[str] = None, 
                    details: Optional[str] = None) -> Optional[int]:
    """
    Records a new trade or withdrawal in the transactions table.
    
    Args:
        user_id: The Telegram user ID.
        tx_type: Type of transaction ('buy', 'sell', etc).
        amount_currency: The currency of the primary amount ('USDT', 'NGN').
        amount: Numerical value of the trade.
        rate: The exchange rate used.
        status: Initial status (usually 'pending').
        tx_hash: Optional blockchain transaction hash.
        details: Metadata such as verified wallet or bank info.
        
    Returns:
        The generated transaction ID or None if the insertion failed.
    """
    data = {
        'user_id': user_id,
        'type': tx_type,
        'amount_currency': amount_currency,
        'amount': amount,
        'rate': rate,
        'status': status,
        'tx_hash': tx_hash,
        'details': details
    }
    try:
        response = supabase.table('transactions').insert(data).execute()
        if response.data:
            return response.data[0]['id']
    except Exception as e:
        logger.error(f"Error adding transaction for {user_id}: {e}")
    return None

def update_transaction_status(tx_id: int, status: str) -> None:
    """
    Updates the state of an existing transaction.
    
    Args:
        tx_id: The transaction ID.
        status: The new status ('completed', 'failed').
    """
    try:
        supabase.table('transactions').update({'status': status}).eq('id', tx_id).execute()
    except Exception as e:
        logger.error(f"Error updating transaction {tx_id}: {e}")

def get_transaction(tx_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves details for a specific transaction.
    
    Args:
        tx_id: The transaction ID.
        
    Returns:
        Dictionary of transaction data or None.
    """
    try:
        response = supabase.table('transactions').select('*').eq('id', tx_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        logger.error(f"Error fetching transaction {tx_id}: {e}")
    return None

def get_user_transactions(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches the most recent transactions for a user.
    
    Args:
        user_id: The Telegram user ID.
        limit: Maximum number of records to return.
        
    Returns:
        A list of transaction dictionaries.
    """
    try:
        response = supabase.table('transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching history for {user_id}: {e}")
    return []

def get_setting(key: str) -> Optional[str]:
    """
    Retrieves a system-wide setting.
    
    Args:
        key: The setting name.
        
    Returns:
        The setting value as a string or None.
    """
    try:
        response = supabase.table('settings').select('value').eq('key', key).execute()
        if response.data:
            return response.data[0]['value']
    except Exception as e:
        logger.error(f"Error fetching setting {key}: {e}")
    return None

def set_setting(key: str, value: str) -> None:
    """
    Updates or creates a system-wide setting.
    
    Args:
        key: The setting name.
        value: The new value.
    """
    try:
        supabase.table('settings').upsert({'key': key, 'value': str(value)}).execute()
    except Exception as e:
        logger.error(f"Error setting {key}: {e}")

def get_all_users() -> List[int]:
    """
    Retrieves a list of all user IDs in the system.
    
    Returns:
        A list of integers (Telegram user IDs).
    """
    try:
        response = supabase.table('users').select('user_id').execute()
        return [row['user_id'] for row in response.data]
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
    return []
