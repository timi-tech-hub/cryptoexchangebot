"""
Blockchain utilities for interacting with the TRON network (TRC20).
Provides methods for USDT balance checking, transaction monitoring, and verification.
"""

import logging
import time
import requests
from typing import Tuple, Optional, Dict, Any
from config import TRONGRID_API_KEY, YOUR_USDT_WALLET

# Setup logging
logger = logging.getLogger(__name__)

# Constants
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # Official USDT (TRC20) contract address
TRON_API_BASE = "https://api.trongrid.io/v1"

def get_usdt_balance(address: str) -> float:
    """
    Queries the blockchain for the current USDT balance of a given TRC20 address.
    
    Args:
        address: The TRON wallet address to query.
        
    Returns:
        The USDT balance as a float (converted from SUN units).
    """
    url = f"{TRON_API_BASE}/accounts/{address}"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if "data" in data and len(data["data"]) > 0:
            account = data["data"][0]
            # USDT balances are stored within the trc20 list
            for token_map in account.get("trc20", []):
                if USDT_CONTRACT in token_map:
                    return int(token_map[USDT_CONTRACT]) / 1_000_000.0
        return 0.0
    except Exception as e:
        logger.error(f"Failed to fetch USDT balance for {address}: {e}")
        return 0.0

def monitor_incoming_usdt(expected_amount: float, timeout_seconds: int = 300) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Polls the merchant wallet for a specific incoming USDT transfer.
    
    Args:
        expected_amount: The USDT value to look for.
        timeout_seconds: Maximum time to spend polling.
        
    Returns:
        A tuple of (transaction_id, sender_address, actual_amount) if found.
    """
    url = f"{TRON_API_BASE}/accounts/{YOUR_USDT_WALLET}/transactions/trc20"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    start_time = time.time()
    
    logger.info(f"Monitoring wallet {YOUR_USDT_WALLET} for {expected_amount} USDT...")
    
    while time.time() - start_time < timeout_seconds:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for tx in data.get("data", []):
                    # Filter for USDT Transfers to the merchant wallet
                    if (tx.get("type") == "Transfer" and 
                        tx.get("token_info", {}).get("address") == USDT_CONTRACT):
                        
                        value = int(tx.get("value", 0)) / 1_000_000.0
                        tx_hash = tx.get("transaction_id")
                        from_addr = tx.get("from")
                        
                        # Match amount with 0.01 tolerance
                        if abs(value - expected_amount) < 0.01:
                            logger.info(f"Matched incoming USDT: {tx_hash}")
                            return tx_hash, from_addr, value
            
            time.sleep(15) # Wait before next poll to stay within API limits
        except Exception as e:
            logger.error(f"Error during blockchain monitoring: {e}")
            time.sleep(15)
            
    return None, None, None

def verify_transaction(tx_hash: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves full transaction metadata from TronGrid.
    
    Args:
        tx_hash: The unique transaction identifier.
        
    Returns:
        The raw transaction data dictionary if found.
    """
    url = f"{TRON_API_BASE}/transactions/{tx_hash}"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]
        return None
    except Exception as e:
        logger.error(f"Failed to verify transaction {tx_hash}: {e}")
        return None

def verify_usdt_deposit(tx_hash: str, expected_amount: float) -> Tuple[Optional[str], Optional[float]]:
    """
    Validates a specific USDT deposit by checking its existence in the blockchain history.
    
    Args:
        tx_hash: The user-provided transaction ID.
        expected_amount: The USDT value expected for the order.
        
    Returns:
        A tuple of (sender_address, actual_amount) if the deposit is verified.
    """
    url = f"{TRON_API_BASE}/accounts/{YOUR_USDT_WALLET}/transactions/trc20"
    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for tx in data.get("data", []):
                if tx.get("transaction_id") == tx_hash:
                    # Validate contract and direction
                    if (tx.get("to") == YOUR_USDT_WALLET and 
                        tx.get("token_info", {}).get("address") == USDT_CONTRACT):
                        
                        value = int(tx.get("value", 0)) / 1_000_000.0
                        from_addr = tx.get("from")
                        
                        if abs(value - expected_amount) < 0.01:
                            return from_addr, value
        return None, None
    except Exception as e:
        logger.error(f"Blockchain deposit verification failed for {tx_hash}: {e}")
        return None, None

def send_usdt(to_address: str, amount_usdt: float, private_key: str) -> str:
    """
    Initiates a USDT transfer from the merchant wallet to a user's address.
    
    🚨 SECURITY WARNING: 
    This is a stub. Production-grade token sending requires a robust signing service.
    Integrating with 'tronpy' or 'tronweb' is recommended for actual signing.
    
    Args:
        to_address: Recipient's TRC20 address.
        amount_usdt: Value to transfer.
        private_key: The signing key for the source wallet.
        
    Raises:
        NotImplementedError: Until a secure signing library is integrated.
    """
    raise NotImplementedError(
        "USDT automated settlement requires integration with a TRON signing library (e.g., tronpy).\n"
        "Manual fulfillment is currently enforced for security."
    )
