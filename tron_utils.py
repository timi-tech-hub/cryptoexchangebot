import requests
import time
from config import TRONGRID_API_KEY, YOUR_USDT_WALLET

USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # USDT (TRC20) mainnet contract

def get_usdt_balance(address):
    """Get USDT balance for a given TRC20 address"""
    url = f"https://api.trongrid.io/v1/accounts/{address}"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if "data" in data and len(data["data"]) > 0:
            account = data["data"][0]
            for token in account.get("trc20", []):
                if USDT_CONTRACT in token:
                    return int(token[USDT_CONTRACT]) / 1_000_000
        return 0.0
    except Exception as e:
        print(f"Error getting USDT balance: {e}")
        return 0.0

def monitor_incoming_usdt(expected_amount, timeout_seconds=300):
    """
    Polls YOUR_USDT_WALLET every 10 seconds for incoming USDT transfers.
    Returns (tx_hash, from_address, actual_amount) if found, else (None, None, None).
    """
    url = f"https://api.trongrid.io/v1/accounts/{YOUR_USDT_WALLET}/transactions/trc20"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            
            if "data" in data:
                for tx in data.get("data", []):
                    # Check if it's a USDT transfer TO your wallet
                    if (tx.get("type") == "Transfer" and 
                        tx.get("token_info", {}).get("address") == USDT_CONTRACT):
                        
                        to_addr = tx.get("to")
                        from_addr = tx.get("from")
                        value = int(tx.get("value", 0)) / 1_000_000
                        tx_hash = tx.get("transaction_id")
                        
                        # Check if amount matches (with small tolerance)
                        if value >= expected_amount - 0.01 and to_addr:
                            return (tx_hash, from_addr, value)
            
            time.sleep(10)
        except Exception as e:
            print(f"Error monitoring USDT: {e}")
            time.sleep(10)
    
    return (None, None, None)

def verify_transaction(tx_hash):
    """Verify a transaction on TronGrid"""
    url = f"https://api.trongrid.io/v1/transactions/{tx_hash}"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]
        return None
    except Exception as e:
        print(f"Error verifying transaction: {e}")
        return None

def verify_usdt_deposit(tx_hash, expected_amount):
    """
    Verify a USDT deposit transaction hash against YOUR_USDT_WALLET.
    Returns (from_address, actual_amount) if valid, else (None, None).
    """
    url = f"https://api.trongrid.io/v1/accounts/{YOUR_USDT_WALLET}/transactions/trc20"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for tx in data.get("data", []):
                if tx.get("transaction_id") == tx_hash:
                    # Check if it's a USDT transfer to our wallet
                    if (tx.get("to") == YOUR_USDT_WALLET and 
                        tx.get("type") == "Transfer" and 
                        tx.get("token_info", {}).get("address") == USDT_CONTRACT):
                        
                        value = int(tx.get("value", 0)) / 1_000_000
                        from_addr = tx.get("from")
                        
                        # Verify amount matches (with small tolerance)
                        if value >= expected_amount - 0.01:
                            return from_addr, value
        return None, None
    except Exception as e:
        print(f"Error verifying USDT deposit: {e}")
        return None, None

def send_usdt(to_address, amount_usdt, private_key):
    """
    Send USDT from your wallet to user.
    
    ⚠️ IMPORTANT: This is complex and requires proper TronWeb/TronPython implementation.
    For security and reliability, consider using:
    - Tron-Python library with proper key management
    - A custodial service API (Binance, Kraken, etc.)
    - A dedicated hot wallet service
    
    This is a placeholder that raises NotImplementedError.
    """
    raise NotImplementedError(
        "USDT sending not yet implemented. Implement using tron-python or a custodial API.\n"
        "For security, never hardcode private keys. Use environment variables or key management services."
    )
