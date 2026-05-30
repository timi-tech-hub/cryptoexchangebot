"""
Blockchain utilities for interacting with the TRON network (TRC20).

This module provides methods for querying USDT balances, monitoring incoming transfers,
verifying transactions, and (template) initiating outgoing payments on the TRON blockchain.

All blockchain interactions use the TronGrid API for reliable data retrieval.
"""

import logging
import time
import requests
from typing import Tuple, Optional, Dict, Any

from config import TRONGRID_API_KEY, YOUR_USDT_WALLET

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# BLOCKCHAIN CONSTANTS
# ============================================================================

# Official USDT (TRC20) contract address on TRON mainnet
USDT_CONTRACT: str = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

# TronGrid API base URL for blockchain queries
TRON_API_BASE: str = "https://api.trongrid.io/v1"

# Request timeout in seconds
REQUEST_TIMEOUT: int = 10

# Polling interval in seconds (respect API rate limits)
POLLING_INTERVAL: int = 15


def get_usdt_balance(address: str) -> float:
    """
    Query the blockchain for the current USDT balance of a TRC20 address.

    Args:
        address: The TRON wallet address to query (format: T...).

    Returns:
        The USDT balance as a float, in standard units (not SUN).
        Returns 0.0 if the query fails.
    """
    url = f"{TRON_API_BASE}/accounts/{address}"
    headers = (
        {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    )

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            account = data["data"][0]
            # USDT balances are stored in the trc20 list
            for token_map in account.get("trc20", []):
                if USDT_CONTRACT in token_map:
                    # Convert from SUN (1 USDT = 1,000,000 SUN)
                    usdt_sun = int(token_map[USDT_CONTRACT])
                    return usdt_sun / 1_000_000.0
        return 0.0
    except requests.exceptions.RequestException as e:
        logger.error(f"Blockchain Error: Failed to fetch USDT balance for {address}: {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Blockchain Error: Unexpected error querying balance: {e}")
        return 0.0


def monitor_incoming_usdt(
    expected_amount: float, timeout_seconds: int = 300
) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """
    Poll the merchant wallet for an incoming USDT transfer of a specific amount.

    This function continuously queries the blockchain until it finds a matching transfer
    or the timeout expires. Use for automated payment verification.

    Args:
        expected_amount: The USDT amount to match (in standard units).
        timeout_seconds: Maximum polling duration in seconds. Defaults to 300 (5 min).

    Returns:
        A tuple of (transaction_id, sender_address, actual_amount) if found,
        or (None, None, None) if timeout or error occurs.

    Note:
        - The function respects blockchain API rate limits (15-second intervals)
        - Matching uses 0.01 USDT tolerance for precision
        - All amounts are in standard USDT units (not SUN)
    """
    url = f"{TRON_API_BASE}/accounts/{YOUR_USDT_WALLET}/transactions/trc20"
    headers = (
        {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    )
    start_time = time.time()

    logger.info(
        f"Blockchain: Monitoring wallet {YOUR_USDT_WALLET} for {expected_amount} USDT..."
    )

    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                for tx in data.get("data", []):
                    # Filter for USDT transfers to the merchant wallet
                    if (
                        tx.get("type") == "Transfer"
                        and tx.get("token_info", {}).get("address") == USDT_CONTRACT
                    ):
                        # Convert from SUN to standard USDT units
                        value = int(tx.get("value", 0)) / 1_000_000.0
                        tx_hash = tx.get("transaction_id")
                        from_addr = tx.get("from")

                        # Match amount with 0.01 tolerance
                        if abs(value - expected_amount) < 0.01:
                            logger.info(
                                f"Blockchain: Matched incoming USDT: {tx_hash} from {from_addr}"
                            )
                            return tx_hash, from_addr, value

            time.sleep(POLLING_INTERVAL)  # Respect API rate limits
        except requests.exceptions.RequestException as e:
            logger.error(f"Blockchain Error: Request failed during monitoring: {e}")
            time.sleep(POLLING_INTERVAL)
        except Exception as e:
            logger.error(f"Blockchain Error: Unexpected error during monitoring: {e}")
            time.sleep(POLLING_INTERVAL)

    logger.warning(
        f"Blockchain: Timeout monitoring for {expected_amount} USDT after {timeout_seconds}s"
    )
    return None, None, None


def verify_transaction(tx_hash: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve full metadata for a transaction from the blockchain.

    Args:
        tx_hash: The unique transaction identifier (transaction_id).

    Returns:
        The raw transaction data dictionary if found, or None if not found/error.

    Note:
        This returns the full transaction object from TronGrid API.
        Useful for comprehensive verification and audit purposes.
    """
    url = f"{TRON_API_BASE}/transactions/{tx_hash}"
    headers = (
        {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    )

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Blockchain Error: Failed to verify transaction {tx_hash}: {e}")
        return None
    except Exception as e:
        logger.error(f"Blockchain Error: Unexpected error verifying transaction: {e}")
        return None


def verify_usdt_deposit(
    tx_hash: str, expected_amount: float
) -> Tuple[Optional[str], Optional[float]]:
    """
    Validate that a specific USDT deposit was received by checking blockchain history.

    This function verifies that:
    1. The transaction exists in the blockchain
    2. It was sent to the merchant wallet
    3. The amount matches the expected value (within tolerance)

    Args:
        tx_hash: The user-provided transaction ID for validation.
        expected_amount: The USDT value expected for the order (in standard units).

    Returns:
        A tuple of (sender_address, actual_amount) if validation succeeds,
        or (None, None) if validation fails or error occurs.

    Note:
        Uses 0.01 USDT tolerance for matching to account for precision.
    """
    url = f"{TRON_API_BASE}/accounts/{YOUR_USDT_WALLET}/transactions/trc20"
    headers = (
        {"TRON-PRO-API-KEY": TRONGRID_API_KEY} if TRONGRID_API_KEY else {}
    )

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            for tx in data.get("data", []):
                if tx.get("transaction_id") == tx_hash:
                    # Validate contract and direction
                    if (
                        tx.get("to") == YOUR_USDT_WALLET
                        and tx.get("token_info", {}).get("address")
                        == USDT_CONTRACT
                    ):
                        # Convert from SUN to standard USDT units
                        value = int(tx.get("value", 0)) / 1_000_000.0
                        from_addr = tx.get("from")

                        if abs(value - expected_amount) < 0.01:
                            logger.info(
                                f"Blockchain: Deposit verified - {value} USDT from {from_addr}"
                            )
                            return from_addr, value
        return None, None
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Blockchain Error: Failed to verify deposit {tx_hash}: {e}"
        )
        return None, None
    except Exception as e:
        logger.error(f"Blockchain Error: Unexpected error verifying deposit: {e}")
        return None, None


def send_usdt(to_address: str, amount_usdt: float, private_key: str) -> str:
    """
    Initiate a USDT transfer from the merchant wallet to a user's address.

    🚨 **SECURITY WARNING**

    This is a stub function. Sending USDT requires secure transaction signing with
    private keys. Production implementation requires:

    1. **Use a Signing Service** (recommended)
       - Never store private keys in code or environment
       - Use AWS KMS, Google Cloud KMS, or similar HSM services
       - Implement hardware wallet integration if possible

    2. **Library Integration**
       - Use 'tronpy' for TRON transaction signing
       - Use 'tronweb.js' (Node.js) or similar for web integration

    3. **Testing First**
       - Always test on testnet before production
       - Implement dry-run/preview mode

    Args:
        to_address: Recipient's TRC20 address (format: T...).
        amount_usdt: Amount to transfer (in standard USDT units, not SUN).
        private_key: Private key for transaction signing (MUST be secured).

    Raises:
        NotImplementedError: Until a secure signing library is integrated.

    Example (for reference, DO NOT use in production):
        from tronpy import Tron
        client = Tron(provider='https://api.trongrid.io')
        txn = client.trx.send(to_address, amount_usdt * 1_000_000)
    """
    raise NotImplementedError(
        "USDT automated settlement requires secure transaction signing.\n"
        "Currently, manual fulfillment is enforced for security.\n"
        "Production: Integrate tronpy, tronweb, or use hardware wallet signing service."
    )
