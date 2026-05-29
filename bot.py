"""
CryptoSwap Telegram Bot - USDT/Naira Exchange Bot
Allows users to buy/sell USDT for Naira, manage balances, and withdraw funds.
"""

import asyncio
import logging
import sqlite3
import requests
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
from telegram.error import TelegramError

from config import BOT_TOKEN, ADMIN_IDS, YOUR_BANK_NAME, YOUR_BANK_ACCOUNT, YOUR_BANK_ACCOUNT_NAME, YOUR_USDT_WALLET
from database import (
    init_db, get_user, register_user, update_balance, add_transaction,
    update_transaction_status, get_setting, set_setting, get_user_transactions,
    get_transaction, get_all_users, auto_create_user, DB_PATH
)
from tron_utils import monitor_incoming_usdt, verify_transaction, get_usdt_balance, verify_usdt_deposit, send_usdt
from responses import get_text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Conversation states
(
    BUY_AMOUNT, BUY_WALLET, BUY_CONFIRM_WALLET, BUY_PAYMENT_PROOF,
    SELL_AMOUNT, SELL_BANK_DETAILS, SELL_CONFIRM_ACC, SELL_TX_HASH
) = range(8)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    return user_id in ADMIN_IDS

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user_id = update.effective_user.id
    auto_create_user(user_id)
    await update.message.reply_text(get_text("WELCOME"), parse_mode="Markdown")

async def handle_general_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general text messages like 'hi'"""
    await start(update, context)

# ============================================================================
# RATES
# ============================================================================

async def rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current exchange rates"""
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
# BUY FLOW (User buys USDT from me)
# ============================================================================

async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start buy flow"""
    await update.message.reply_text(get_text("BUY_START"), parse_mode="Markdown")
    return BUY_AMOUNT

async def buy_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buy amount"""
    try:
        amount = float(update.message.text)
        if amount <= 0: raise ValueError
    except ValueError:
        await update.message.reply_text(get_text("INVALID_AMOUNT"), parse_mode="Markdown")
        return BUY_AMOUNT
    
    context.user_data['buy_amount'] = amount
    await update.message.reply_text(get_text("BUY_AMOUNT_SUCCESS", amount=amount), parse_mode="Markdown")
    return BUY_WALLET

async def buy_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buy wallet address"""
    wallet = update.message.text.strip()
    if not (wallet.startswith('T') and len(wallet) == 34):
        await update.message.reply_text(get_text("BUY_WALLET_INVALID"), parse_mode="Markdown")
        return BUY_WALLET
    
    context.user_data['buy_wallet'] = wallet
    await update.message.reply_text(get_text("BUY_WALLET_DOUBLE_CHECK"), parse_mode="Markdown")
    return BUY_CONFIRM_WALLET

async def buy_confirm_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buy wallet confirmation"""
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

async def buy_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buy payment proof and notify admin"""
    sell_rate = int(get_setting('sell_rate') or 1520)
    amount = context.user_data['buy_amount']
    wallet = context.user_data['buy_wallet']
    naira = amount * sell_rate
    user_id = update.effective_user.id
    
    # Create transaction record
    tx_id = add_transaction(
        user_id=user_id,
        tx_type='buy',
        amount_currency='USDT',
        amount=amount,
        rate=sell_rate,
        status='pending',
        details=f"Wallet: {wallet}"
    )
    
    admin_msg = (
        f"🚨 *NEW BUY ORDER #{tx_id}*\n\n"
        f"User: `{user_id}`\n"
        f"Buy Amount: {amount} USDT\n"
        f"Pay Amount: ₦{naira:,.2f}\n"
        f"🎯 *Recipient Wallet:* `{wallet}`"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approved (I Sent Crypto)", callback_data=f"admin_approve_{tx_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{tx_id}")
        ]
    ])
    
    if update.message.photo:
        await context.bot.send_photo(chat_id=ADMIN_IDS[0], photo=update.message.photo[-1].file_id, caption=admin_msg, parse_mode="Markdown", reply_markup=keyboard)
    elif update.message.document:
        await context.bot.send_document(chat_id=ADMIN_IDS[0], document=update.message.document.file_id, caption=admin_msg, parse_mode="Markdown", reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=ADMIN_IDS[0], text=admin_msg + f"\n\nNote: {update.message.text}", parse_mode="Markdown", reply_markup=keyboard)
        
    await update.message.reply_text(get_text("BUY_ORDER_COMPLETE", tx_id=tx_id), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

# ============================================================================
# SELL FLOW (User sells USDT to me)
# ============================================================================

async def sell_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start sell flow"""
    await update.message.reply_text(get_text("SELL_START"), parse_mode="Markdown")
    return SELL_AMOUNT

async def sell_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sell amount"""
    try:
        amount = float(update.message.text)
        if amount <= 0: raise ValueError
    except ValueError:
        await update.message.reply_text(get_text("INVALID_AMOUNT"), parse_mode="Markdown")
        return SELL_AMOUNT
    
    context.user_data['sell_amount'] = amount
    await update.message.reply_text(get_text("SELL_AMOUNT_SUCCESS", amount=amount), parse_mode="Markdown")
    return SELL_BANK_DETAILS

async def sell_bank_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sell bank details"""
    details = update.message.text.strip()
    import re
    acc_num = re.search(r'\d{10}', details)
    if not acc_num:
        await update.message.reply_text(get_text("SELL_BANK_INVALID"), parse_mode="Markdown")
        return SELL_BANK_DETAILS
    
    context.user_data['sell_bank'] = details
    context.user_data['sell_acc_num'] = acc_num.group(0)
    await update.message.reply_text(get_text("SELL_BANK_DOUBLE_CHECK"), parse_mode="Markdown")
    return SELL_CONFIRM_ACC

async def sell_confirm_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sell account confirmation"""
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

async def sell_tx_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sell TX hash and notify admin"""
    tx_hash = update.message.text.strip()
    buy_rate = int(get_setting('buy_rate') or 1480)
    amount = context.user_data['sell_amount']
    bank_details = context.user_data['sell_bank']
    naira = amount * buy_rate
    user_id = update.effective_user.id
    
    # Create transaction record
    tx_id = add_transaction(
        user_id=user_id,
        tx_type='sell',
        amount_currency='USDT',
        amount=amount,
        rate=buy_rate,
        status='pending',
        tx_hash=tx_hash,
        details=f"Bank: {bank_details}"
    )
    
    admin_msg = (
        f"🚨 *NEW SELL ORDER #{tx_id}*\n\n"
        f"User: `{user_id}`\n"
        f"Sell Amount: {amount} USDT\n"
        f"Pay Amount: ₦{naira:,.2f}\n"
        f"🏦 *Bank Details:* {bank_details}\n"
        f"🔗 *TXID:* `{tx_hash}`"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approved (I Paid User)", callback_data=f"admin_approve_{tx_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{tx_id}")
        ]
    ])
    
    await context.bot.send_message(chat_id=ADMIN_IDS[0], text=admin_msg, parse_mode="Markdown", reply_markup=keyboard)
    await update.message.reply_text(get_text("SELL_ORDER_COMPLETE", tx_id=tx_id), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current conversation"""
    await update.message.reply_text(get_text("CANCEL_TRADE"), parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

# ============================================================================
# ADMIN HANDLER
# ============================================================================

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin approval/rejection callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("❌ Unauthorized.", show_alert=True)
        return
        
    data = query.data
    parts = data.split('_')
    action = parts[1]
    tx_id = int(parts[2])
    
    tx = get_transaction(tx_id)
    if not tx:
        await query.edit_message_text("❌ Transaction not found.")
        return
        
    if tx['status'] != 'pending':
        await query.edit_message_text(f"❌ Transaction already {tx['status']}.")
        return
        
    tx_user_id = tx['user_id']
    
    if action == 'approve':
        update_transaction_status(tx_id, 'completed')
        await query.edit_message_text(f"✅ Order #{tx_id} marked as COMPLETED.")
        
        try:
            await context.bot.send_message(
                chat_id=tx_user_id,
                text=f"✅ *Order #{tx_id} Completed!*\n\n"
                     f"Your trade has been verified and processed. Thank you for trading with us!",
                parse_mode="Markdown"
            )
        except TelegramError:
            pass
            
    elif action == 'reject':
        update_transaction_status(tx_id, 'failed')
        await query.edit_message_text(f"❌ Order #{tx_id} REJECTED.")
        
        try:
            await context.bot.send_message(
                chat_id=tx_user_id,
                text=f"❌ *Order #{tx_id} Rejected*\n\n"
                     f"Your transaction was not verified or contains errors. Please contact support.",
                parse_mode="Markdown"
            )
        except TelegramError:
            pass

# ============================================================================
# HISTORY & SUPPORT
# ============================================================================

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show transaction history"""
    txs = get_user_transactions(update.effective_user.id, limit=10)
    if not txs:
        await update.message.reply_text(get_text("HISTORY_EMPTY"), parse_mode="Markdown")
        return
    
    msg = "📊 *Last 10 Transactions*\n\n"
    for tx in txs:
        status_emoji = "✅" if tx['status'] == "completed" else "⏳" if tx['status'] == "pending" else "❌"
        msg += f"{status_emoji} {tx['type'].upper()} | {tx['amount']:.2f} {tx['amount_currency']} @ ₦{tx['rate']} | {tx['created_at'][:10]}\n"
    
    await update.message.reply_text(msg, parse_mode="Markdown")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Support/contact info"""
    admin_id = ADMIN_IDS[0]
    await update.message.reply_text(get_text("SUPPORT", admin_id=admin_id), parse_mode="Markdown")

# ============================================================================
# ADMIN COMMANDS
# ============================================================================

async def setrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set exchange rates (admin only)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    args = context.args
    if len(args) != 2:
        await update.message.reply_text(
            "Usage: `/setrate <buy_rate> <sell_rate>`\n"
            "Example: `/setrate 1480 1520`",
            parse_mode="Markdown"
        )
        return
    
    try:
        buy_rate = int(args[0])
        sell_rate = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Rates must be integers.")
        return
    
    if sell_rate <= buy_rate:
        await update.message.reply_text("❌ Sell rate must be higher than buy rate.")
        return
    
    set_setting('buy_rate', str(buy_rate))
    set_setting('sell_rate', str(sell_rate))
    
    await update.message.reply_text(
        f"✅ Rates updated:\n\n"
        f"📈 I Buy: ₦{buy_rate}/USDT\n"
        f"📉 I Sell: ₦{sell_rate}/USDT\n"
        f"Spread: ₦{sell_rate - buy_rate}",
        parse_mode="Markdown"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users (admin only)"""
    if not is_admin(update.effective_user.id):
        return
    
    message = ' '.join(context.args)
    if not message:
        await update.message.reply_text("Usage: `/broadcast <message>`", parse_mode="Markdown")
        return
    
    users = get_all_users()
    sent = 0
    failed = 0
    
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 *Announcement*\n\n{message}",
                parse_mode="Markdown"
            )
            sent += 1
            await asyncio.sleep(0.05)
        except TelegramError:
            failed += 1
    
    await update.message.reply_text(
        f"✅ Broadcast complete.\n"
        f"Sent: {sent} | Failed: {failed}",
        parse_mode="Markdown"
    )

# ============================================================================
# PERIODIC REMINDERS
# ============================================================================

async def send_reminder_broadcast(context: ContextTypes.DEFAULT_TYPE):
    """Send a reminder message to all users"""
    users = get_all_users()
    sent = 0
    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=get_text("REMINDER"),
                parse_mode="Markdown"
            )
            sent += 1
            await asyncio.sleep(0.05)
        except TelegramError:
            pass
    
    logger.info(f"Periodic reminder sent to {sent} users.")
    set_setting('last_reminder_date', datetime.now().strftime('%Y-%m-%d'))

async def reminder_scheduler(app: Application):
    """Background task to check if it is time for a reminder (every 90 days)"""
    while True:
        last_date_str = get_setting('last_reminder_date')
        should_send = False
        
        if not last_date_str:
            set_setting('last_reminder_date', datetime.now().strftime('%Y-%m-%d'))
        else:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            days_passed = (datetime.now() - last_date).days
            if days_passed >= 90:
                should_send = True
        
        if should_send:
            logger.info("Triggering 3-month periodic reminder...")
            users = get_all_users()
            for user_id in users:
                try:
                    await app.bot.send_message(chat_id=user_id, text=get_text("REMINDER"), parse_mode="Markdown")
                    await asyncio.sleep(0.05)
                except Exception:
                    continue
            
            set_setting('last_reminder_date', datetime.now().strftime('%Y-%m-%d'))
        
        await asyncio.sleep(86400)

# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ============================================================================
# MAIN
# ============================================================================

async def post_init(app: Application):
    """Start background tasks after bot is initialized"""
    asyncio.create_task(reminder_scheduler(app))

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Conversation Handlers for Buy and Sell
    buy_conv = ConversationHandler(
        entry_points=[
            CommandHandler("buy", buy_start),
            MessageHandler(filters.Regex(r'^(?i)buy'), buy_start)
        ],
        states={
            BUY_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_amount)],
            BUY_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_wallet)],
            BUY_CONFIRM_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_confirm_wallet)],
            BUY_PAYMENT_PROOF: [MessageHandler(filters.PHOTO | filters.Document.ALL | filters.TEXT, buy_payment_proof)],
        },
        fallbacks=[CommandHandler("cancel", cancel_trade), MessageHandler(filters.Regex(r'^(?i)cancel'), cancel_trade)],
    )
    
    sell_conv = ConversationHandler(
        entry_points=[
            CommandHandler("sell", sell_start),
            MessageHandler(filters.Regex(r'^(?i)sell'), sell_start)
        ],
        states={
            SELL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_amount)],
            SELL_BANK_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_bank_details)],
            SELL_CONFIRM_ACC: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_confirm_acc)],
            SELL_TX_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_tx_hash)],
        },
        fallbacks=[CommandHandler("cancel", cancel_trade), MessageHandler(filters.Regex(r'^(?i)cancel'), cancel_trade)],
    )
    
    # Register handlers
    app.add_handler(buy_conv)
    app.add_handler(sell_conv)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rates", rates))
    app.add_handler(MessageHandler(filters.Regex(r'^(?i)(rate|price)'), rates))
    
    app.add_handler(CommandHandler("history", history))
    app.add_handler(MessageHandler(filters.Regex(r'^(?i)(history|order|transaction)'), history))
    
    app.add_handler(CommandHandler("support", support))
    app.add_handler(MessageHandler(filters.Regex(r'^(?i)(support|help|admin)'), support))
    
    # Admin commands
    app.add_handler(CommandHandler("setrate", setrate))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_admin_callback, pattern="^admin_"))
    
    # General text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_general_text))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    logger.info("🤖 P2P Crypto Exchange Bot started...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ CRITICAL BOT CRASH: {e}", exc_info=True)
        import sys
        sys.exit(1)
