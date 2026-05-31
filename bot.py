"""
Main entry point for the Nigerian P2P Crypto Exchange Telegram Bot.
Orchestrates conversation flows, admin fulfillment, and background reminder tasks.
"""

import asyncio
import logging
import re
import sys
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from typing import NoReturn, Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
from telegram.error import TelegramError

# Local module imports
from config import (
    BOT_TOKEN, ADMIN_IDS, YOUR_BANK_NAME, YOUR_BANK_ACCOUNT, 
    YOUR_BANK_ACCOUNT_NAME, YOUR_USDT_WALLET
)
from database import (
    init_db, get_user, register_user, update_balance, add_transaction,
    update_transaction_status, get_setting, set_setting, get_user_transactions,
    get_transaction, get_all_users, auto_create_user
)
from utils.tron_utils import (
    monitor_incoming_usdt, verify_transaction, get_usdt_balance, 
    verify_usdt_deposit, send_usdt
)
from responses import get_text

# Setup logging with a professional format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Conversation State Constants ---
(
    BUY_AMOUNT, BUY_WALLET, BUY_CONFIRM_WALLET, BUY_PAYMENT_PROOF,
    SELL_AMOUNT, SELL_BANK_DETAILS, SELL_CONFIRM_ACC, SELL_TX_HASH
) = range(8)

# ============================================================================
# INFRASTRUCTURE: HEALTH CHECK SERVER
# ============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler to satisfy Render's port binding requirement."""
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot Service Active")

    def log_message(self, format: str, *args: Any) -> None:
        return # Silence server logs for clarity

def run_dummy_server() -> None:
    """Starts a background HTTP server for health checks."""
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        logger.info(f"🌐 Infrastructure: Health-check server active on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"❌ Infrastructure: Failed to start health-check server: {e}")

# ============================================================================
# SECURITY & HELPERS
# ============================================================================

def is_admin(user_id: int) -> bool:
    """Validates if a user has administrative privileges."""
    return user_id in ADMIN_IDS

# ============================================================================
# INTERFACE: CORE COMMANDS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Initializes the user profile and displays the welcome interface."""
    user_id = update.effective_user.id
    auto_create_user(user_id)
    await update.message.reply_text(get_text("WELCOME"), parse_mode="Markdown")

async def handle_general_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Redirects unrecognized text to the start menu."""
    await start(update, context)

async def rates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays current USDT/NGN exchange rates fetched from settings."""
    buy_rate = int(get_setting('buy_rate') or 1480)
    sell_rate = int(get_setting('sell_rate') or 1520)
    
    header = get_text("RATES_HEADER")
    msg = (
        f"{header}\n\n"
        f"📈 *I Buy USDT* (you sell to me): ₦{buy_rate}/USDT\n"
        f"📉 *I Sell USDT* (you buy from me): ₦{sell_rate}/USDT\n\n"
        f"Type 'buy' or 'sell' to start a trade."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# ============================================================================
# FLOW: BUY USDT (Naira to Crypto)
# ============================================================================

async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the USDT purchase conversation."""
    await update.message.reply_text(get_text("BUY_START"), parse_mode="Markdown")
    return BUY_AMOUNT

async def buy_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validates and records the requested purchase amount."""
    try:
        amount = float(update.message.text)
        if amount <= 0: raise ValueError
    except ValueError:
        await update.message.reply_text(get_text("INVALID_AMOUNT"), parse_mode="Markdown")
        return BUY_AMOUNT
    
    context.user_data['buy_amount'] = amount
    await update.message.reply_text(get_text("BUY_AMOUNT_SUCCESS", amount=amount), parse_mode="Markdown")
    return BUY_WALLET

async def buy_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collects and performs initial validation on the user's TRC20 wallet."""
    wallet = update.message.text.strip()
    if not (wallet.startswith('T') and len(wallet) == 34):
        await update.message.reply_text(get_text("BUY_WALLET_INVALID"), parse_mode="Markdown")
        return BUY_WALLET
    
    context.user_data['buy_wallet'] = wallet
    await update.message.reply_text(get_text("BUY_WALLET_DOUBLE_CHECK"), parse_mode="Markdown")
    return BUY_CONFIRM_WALLET

async def buy_confirm_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Performs the secondary confirmation (double-entry) for the wallet address."""
    wallet_confirm = update.message.text.strip()
    if wallet_confirm != context.user_data['buy_wallet']:
        await update.message.reply_text(get_text("WALLET_MISMATCH"), parse_mode="Markdown")
        return BUY_WALLET
    
    sell_rate = int(get_setting('sell_rate') or 1520)
    naira_total = context.user_data['buy_amount'] * sell_rate
    
    await update.message.reply_text(
        get_text(
            "BUY_PAYMENT_DETAILS",
            amount=context.user_data['buy_amount'],
            naira=naira_total,
            bank=YOUR_BANK_NAME,
            acc=YOUR_BANK_ACCOUNT,
            name=YOUR_BANK_ACCOUNT_NAME
        ),
        parse_mode="Markdown"
    )
    return BUY_PAYMENT_PROOF

async def buy_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes payment proof and notifies administrators for manual verification."""
    sell_rate = int(get_setting('sell_rate') or 1520)
    amount = context.user_data['buy_amount']
    wallet = context.user_data['buy_wallet']
    naira = amount * sell_rate
    user_id = update.effective_user.id
    
    # Record transaction intent
    tx_id = add_transaction(
        user_id=user_id,
        tx_type='buy',
        amount_currency='USDT',
        amount=amount,
        rate=sell_rate,
        status='pending',
        details=f"Recipient Wallet: {wallet}"
    )
    
    admin_msg = (
        f"🚨 *TRADE: BUY ORDER #{tx_id}*\n\n"
        f"Client ID: `{user_id}`\n"
        f"Requested: {amount} USDT\n"
        f"Expected: ₦{naira:,.2f}\n"
        f"🎯 *Target Wallet:* `{wallet}`"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approved (Credit User)", callback_data=f"admin_approve_{tx_id}"),
            InlineKeyboardButton("❌ Reject (Wait)", callback_data=f"admin_reject_{tx_id}")
        ]
    ])
    
    # Forward proof to the first configured admin
    if update.message.photo:
        await context.bot.send_photo(chat_id=ADMIN_IDS[0], photo=update.message.photo[-1].file_id, caption=admin_msg, parse_mode="Markdown", reply_markup=keyboard)
    elif update.message.document:
        await context.bot.send_document(chat_id=ADMIN_IDS[0], document=update.message.document.file_id, caption=admin_msg, parse_mode="Markdown", reply_markup=keyboard)
    else:
        note = update.message.text or "No text provided"
        await context.bot.send_message(chat_id=ADMIN_IDS[0], text=f"{admin_msg}\n\nNote: {note}", parse_mode="Markdown", reply_markup=keyboard)
        
    await update.message.reply_text(get_text("BUY_ORDER_COMPLETE", tx_id=tx_id), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

# ============================================================================
# FLOW: SELL USDT (Crypto to Naira)
# ============================================================================

async def sell_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the USDT sale conversation."""
    await update.message.reply_text(get_text("SELL_START"), parse_mode="Markdown")
    return SELL_AMOUNT

async def sell_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validates and records the USDT amount the user wishes to sell."""
    try:
        amount = float(update.message.text)
        if amount <= 0: raise ValueError
    except ValueError:
        await update.message.reply_text(get_text("INVALID_AMOUNT"), parse_mode="Markdown")
        return SELL_AMOUNT
    
    context.user_data['sell_amount'] = amount
    await update.message.reply_text(get_text("SELL_AMOUNT_SUCCESS", amount=amount), parse_mode="Markdown")
    return SELL_BANK_DETAILS

async def sell_bank_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collects target bank account details for Naira settlement."""
    details = update.message.text.strip()
    acc_num_match = re.search(r'\d{10}', details)
    
    if not acc_num_match:
        await update.message.reply_text(get_text("SELL_BANK_INVALID"), parse_mode="Markdown")
        return SELL_BANK_DETAILS
    
    context.user_data['sell_bank'] = details
    context.user_data['sell_acc_num'] = acc_num_match.group(0)
    await update.message.reply_text(get_text("SELL_BANK_DOUBLE_CHECK"), parse_mode="Markdown")
    return SELL_CONFIRM_ACC

async def sell_confirm_acc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Performs the secondary confirmation (double-entry) for the bank account number."""
    acc_confirm = update.message.text.strip()
    if acc_confirm != context.user_data['sell_acc_num']:
        await update.message.reply_text(get_text("ACC_MISMATCH"), parse_mode="Markdown")
        return SELL_BANK_DETAILS
    
    buy_rate = int(get_setting('buy_rate') or 1480)
    naira_total = context.user_data['sell_amount'] * buy_rate
    
    await update.message.reply_text(
        get_text(
            "SELL_INSTRUCTIONS",
            amount=context.user_data['sell_amount'],
            wallet=YOUR_USDT_WALLET
        ),
        parse_mode="Markdown"
    )
    return SELL_TX_HASH

async def sell_tx_hash(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Records the blockchain TXID and alerts administrators for payment processing."""
    tx_hash = update.message.text.strip()
    buy_rate = int(get_setting('buy_rate') or 1480)
    amount = context.user_data['sell_amount']
    bank_details = context.user_data['sell_bank']
    naira = amount * buy_rate
    user_id = update.effective_user.id
    
    # Record transaction intent
    tx_id = add_transaction(
        user_id=user_id,
        tx_type='sell',
        amount_currency='USDT',
        amount=amount,
        rate=buy_rate,
        status='pending',
        tx_hash=tx_hash,
        details=f"Bank Settlement: {bank_details}"
    )
    
    admin_msg = (
        f"🚨 *TRADE: SELL ORDER #{tx_id}*\n\n"
        f"Client ID: `{user_id}`\n"
        f"Selling: {amount} USDT\n"
        f"Payable: ₦{naira:,.2f}\n"
        f"🏦 *Target Bank:* {bank_details}\n"
        f"🔗 *Hash:* `{tx_hash}`"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approved (Paid)", callback_data=f"admin_approve_{tx_id}"),
            InlineKeyboardButton("❌ Reject (Wait)", callback_data=f"admin_reject_{tx_id}")
        ]
    ])
    
    await context.bot.send_message(chat_id=ADMIN_IDS[0], text=admin_msg, parse_mode="Markdown", reply_markup=keyboard)
    await update.message.reply_text(get_text("SELL_ORDER_COMPLETE", tx_id=tx_id), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gracefully terminates an active conversation."""
    await update.message.reply_text(get_text("CANCEL_TRADE"), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

# ============================================================================
# ADMINISTRATION: FULFILLMENT & MANAGEMENT
# ============================================================================

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manages trade approval and rejection logic with state protection (idempotency)."""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.answer("Security Error: Unauthorized access attempt.", show_alert=True)
        return
        
    parts = query.data.split('_')
    action, tx_id = parts[1], int(parts[2])
    
    tx = get_transaction(tx_id)
    if not tx:
        await query.edit_message_text("Data Integrity Error: Transaction record not found.")
        return
        
    # State Guard: Prevent modifications to already finalized trades
    if tx['status'] == 'completed':
        await query.answer("Notice: This order has already been finalized.", show_alert=True)
        return
        
    tx_user_id = tx['user_id']
    
    if action == 'approve':
        update_transaction_status(tx_id, 'completed')
        # Finalize Admin UI (Strip buttons to prevent re-clicks)
        await query.edit_message_text(f"✅ Order #{tx_id} finalized and marked as COMPLETED.")
        
        try:
            await context.bot.send_message(
                chat_id=tx_user_id,
                text=get_text("ADMIN_APPROVE_USER", tx_id=tx_id),
                parse_mode="Markdown"
            )
        except TelegramError as e:
            logger.error(f"Notification failure for user {tx_user_id}: {e}")
            
    elif action == 'reject':
        if tx['status'] == 'failed':
            await query.answer("Notice: Order is already in a rejected state.", show_alert=True)
            return
            
        update_transaction_status(tx_id, 'failed')
        # Allow re-approval if rejection was premature
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Re-approve (Funds Received)", callback_data=f"admin_approve_{tx_id}")]
        ])
        await query.edit_message_text(
            f"❌ Order #{tx_id} REJECTED (Pending funds).\n\nYou may still approve this trade if funds reflect later.",
            reply_markup=keyboard
        )
        
        try:
            await context.bot.send_message(
                chat_id=tx_user_id,
                text=get_text("ADMIN_REJECT_USER", tx_id=tx_id),
                parse_mode="Markdown"
            )
        except TelegramError as e:
            logger.error(f"Notification failure for user {tx_user_id}: {e}")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the authenticated user's recent transaction ledger."""
    txs = get_user_transactions(update.effective_user.id, limit=10)
    if not txs:
        await update.message.reply_text(get_text("HISTORY_EMPTY"), parse_mode="Markdown")
        return
    
    msg = "📊 *Recent P2P Activity*\n\n"
    for tx in txs:
        status_icon = "✅" if tx['status'] == "completed" else "⏳" if tx['status'] == "pending" else "❌"
        date_str = tx['created_at'][:10]
        msg += f"{status_icon} {tx['type'].upper()} | {tx['amount']:.2f} {tx['amount_currency']} | {date_str}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provides human-intervention contact details."""
    admin_id = ADMIN_IDS[0]
    await update.message.reply_text(get_text("SUPPORT", admin_id=admin_id), parse_mode="Markdown")

async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Administrator command to adjust real-time exchange rates."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Permission Denied.")
        return
    
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: `/setrate <buy_price> <sell_price>`")
        return
    
    try:
        buy_rate, sell_rate = int(args[0]), int(args[1])
        if sell_rate <= buy_rate:
            await update.message.reply_text("Market Rule Error: Sell rate must exceed buy rate.")
            return
            
        set_setting('buy_rate', str(buy_rate))
        set_setting('sell_rate', str(sell_rate))
        await update.message.reply_text(f"✅ Rates Synchronized:\n📈 Buy: ₦{buy_rate}\n📉 Sell: ₦{sell_rate}")
    except ValueError:
        await update.message.reply_text("Input Error: Rates must be valid integers.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Administrator command to dispatch a system-wide announcement."""
    if not is_admin(update.effective_user.id): return
    
    message = ' '.join(context.args)
    if not message: return
    
    users = get_all_users()
    sent_count, failed_count = 0, 0
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 *Announcement*\n\n{message}", parse_mode="Markdown")
            sent_count += 1
            await asyncio.sleep(0.05) # Prevent Telegram Rate Limiting
        except TelegramError:
            failed_count += 1
    
    await update.message.reply_text(f"✅ Broadcast Status: {sent_count} Delivered | {failed_count} Blocked")

# ============================================================================
# AUTOMATION: PERIODIC SCHEDULING
# ============================================================================

async def reminder_scheduler(app: Application) -> NoReturn:
    """Background loop ensuring consistent customer engagement (90-day intervals)."""
    while True:
        last_date_str = get_setting('last_reminder_date')
        if not last_date_str:
            set_setting('last_reminder_date', datetime.now().strftime('%Y-%m-%d'))
        else:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            if (datetime.now() - last_date).days >= 90:
                logger.info("Automation: Dispatching periodic engagement reminder...")
                for user_id in get_all_users():
                    try:
                        await app.bot.send_message(chat_id=user_id, text=get_text("REMINDER"), parse_mode="Markdown")
                        await asyncio.sleep(0.05)
                    except Exception: continue
                set_setting('last_reminder_date', datetime.now().strftime('%Y-%m-%d'))
        
        await asyncio.sleep(86400) # Re-check daily

# ============================================================================
# CORE: INITIALIZATION & RUNTIME
# ============================================================================

async def post_init(app: Application) -> None:
    """Handles service startup procedures after bot initialization."""
    asyncio.create_task(reminder_scheduler(app))

async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Centralized exception handling for the bot runtime."""
    logger.error(f"Runtime Error: Update {update} triggered {context.error}")

def main() -> None:
    """Orchestrates the bot service lifecycle."""
    # Initialize Database
    init_db()
    
    # Start Infrastructure Health-Check
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # Initialize Core Application
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # --- Registered Logic Handlers ---
    
    # Transactional Conversations
    buy_conv = ConversationHandler(
        entry_points=[CommandHandler("buy", buy_start), MessageHandler(filters.Regex(r'(?i)^buy'), buy_start)],
        states={
            BUY_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_amount)],
            BUY_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_wallet)],
            BUY_CONFIRM_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_confirm_wallet)],
            BUY_PAYMENT_PROOF: [MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT, buy_payment_proof)],
        },
        fallbacks=[CommandHandler("cancel", cancel_trade), MessageHandler(filters.Regex(r'(?i)^cancel'), cancel_trade)],
    )
    
    sell_conv = ConversationHandler(
        entry_points=[CommandHandler("sell", sell_start), MessageHandler(filters.Regex(r'(?i)^sell'), sell_start)],
        states={
            SELL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_amount)],
            SELL_BANK_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_bank_details)],
            SELL_CONFIRM_ACC: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_confirm_acc)],
            SELL_TX_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_tx_hash)],
        },
        fallbacks=[CommandHandler("cancel", cancel_trade), MessageHandler(filters.Regex(r'(?i)^cancel'), cancel_trade)],
    )
    
    app.add_handler(buy_conv)
    app.add_handler(sell_conv)
    
    # Command & UI Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rates", rates))
    app.add_handler(MessageHandler(filters.Regex(r'(?i)^(rate|price)'), rates))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(MessageHandler(filters.Regex(r'(?i)^(history|order|transaction)'), history))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(MessageHandler(filters.Regex(r'(?i)^(support|help|admin)'), support))
    
    # Admin Control Panel
    app.add_handler(CommandHandler("setrate", setrate))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))
    
    # Catch-all & Infrastructure
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_general_text))
    app.add_error_handler(error_handler)
    
    # Persistent Start
    logger.info("🤖 Runtime: Nigerian P2P Crypto Exchange Bot initialized.")
    
    # Fix for "RuntimeError: There is no current event loop in thread 'MainThread'"
    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"🛑 CRITICAL SYSTEM FAILURE: {e}", exc_info=True)
        sys.exit(1)
