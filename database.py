import os
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
# If these are missing, the bot will fail at startup - which is better for debugging
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    """
    In Supabase, we don't 'init' tables via code usually (handled in dashboard).
    However, we ensure default settings exist.
    """
    # Insert default rates if not exist
    set_setting_if_not_exists('buy_rate', '1480')
    set_setting_if_not_exists('sell_rate', '1520')

def set_setting_if_not_exists(key, value):
    """Helper to set default if not present"""
    existing = get_setting(key)
    if existing is None:
        set_setting(key, value)

def get_user(user_id):
    """Retrieve user details by ID"""
    try:
        response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"Supabase error get_user: {e}")
    return None

def register_user(user_id, phone, bank_name, bank_account_name, bank_account_number, crypto_address):
    """Register a new user or update existing"""
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
        print(f"Supabase error register_user: {e}")

def auto_create_user(user_id):
    """Ensure user exists in DB, create with defaults if not"""
    user = get_user(user_id)
    if not user:
        register_user(user_id, "", "", "", "", "")
        user = get_user(user_id)
    return user

def update_balance(user_id, naira_delta=0, usdt_delta=0):
    """
    Update user's balance. 
    Note: For P2P refactor, this is mostly unused but kept for compatibility.
    In Postgres, we use RPC or atomic increments if possible.
    """
    user = get_user(user_id)
    if not user: return
    
    new_naira = (user.get('naira_balance') or 0) + naira_delta
    new_usdt = (user.get('usdt_balance') or 0) + usdt_delta
    
    try:
        supabase.table('users').update({
            'naira_balance': new_naira,
            'usdt_balance': new_usdt
        }).eq('user_id', user_id).execute()
    except Exception as e:
        print(f"Supabase error update_balance: {e}")

def add_transaction(user_id, tx_type, amount_currency, amount, rate, status, tx_hash=None, details=None):
    """Add a new transaction record"""
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
        print(f"Supabase error add_transaction: {e}")
    return None

def update_transaction_status(tx_id, status):
    """Update transaction status"""
    try:
        supabase.table('transactions').update({'status': status}).eq('id', tx_id).execute()
    except Exception as e:
        print(f"Supabase error update_transaction_status: {e}")

def get_transaction(tx_id):
    """Retrieve transaction details"""
    try:
        response = supabase.table('transactions').select('*').eq('id', tx_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        print(f"Supabase error get_transaction: {e}")
    return None

def get_user_transactions(user_id, limit=10):
    """Get user's transaction history"""
    try:
        response = supabase.table('transactions')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        print(f"Supabase error get_user_transactions: {e}")
    return []

def get_setting(key):
    """Retrieve a setting value"""
    try:
        response = supabase.table('settings').select('value').eq('key', key).execute()
        if response.data:
            return response.data[0]['value']
    except Exception as e:
        print(f"Supabase error get_setting: {e}")
    return None

def set_setting(key, value):
    """Set or update a setting"""
    try:
        supabase.table('settings').upsert({'key': key, 'value': str(value)}).execute()
    except Exception as e:
        print(f"Supabase error set_setting: {e}")

def get_all_users():
    """Get all registered user IDs"""
    try:
        response = supabase.table('users').select('user_id').execute()
        return [row['user_id'] for row in response.data]
    except Exception as e:
        print(f"Supabase error get_all_users: {e}")
    return []
