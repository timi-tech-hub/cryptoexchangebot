# 🤖 Nigerian P2P Crypto Exchange Bot

A specialized Telegram bot for direct P2P exchange of USDT (TRC20) for Nigerian Naira. Built for traders who want a smooth, conversational, and human-like trading experience without the hassle of accounts and balances.

---

## 🇳🇬 Key Features

✅ **Strict P2P Model** - Direct trades (Naira ↔️ Crypto) with no internal balance holding.  
✅ **Human-like Conversations** - 200+ response variations in **Nigerian Pidgin** & slang.  
✅ **Double-Confirmation Security** - Prevents errors by requiring users to enter wallets and account numbers twice.  
✅ **Multi-Step Trading** - Interactive flows for 'buy' and 'sell' requests.  
✅ **3-Month Reminders** - Automatically reminds customers about your services every 90 days.  
✅ **Natural Language Recognition** - Works with normal words like "buy", "sell", "rates" instead of just slash commands.  
✅ **Admin Fulfillment** - Direct approval buttons for manual fulfillment of trades.

---

## 🚀 Quick Start (Deployment on Render)

The easiest way to host this bot is on **Render.com**.

### 1. Get Your Tokens
- **Bot Token**: Message **@BotFather** on Telegram to create your bot.
- **Admin ID**: Message **@userinfobot** to get your numeric ID.
- **TronGrid API Key**: Visit [trongrid.io](https://www.trongrid.io) and create a free key.

### 2. Deploy to Render
1. **Push to GitHub**: Upload these project files to a **Private** repository.
2. **Connect to Render**: Go to Render Dashboard -> **New +** -> **Blueprint** -> Connect your repo.
3. **Environment Variables**: Add these in the Render dashboard:
   - `BOT_TOKEN`: Your Telegram token.
   - `ADMIN_IDS`: Your numeric ID.
   - `TRONGRID_API_KEY`: Your key from Step 1.
   - `YOUR_BANK_NAME`, `YOUR_BANK_ACCOUNT`, `YOUR_BANK_ACCOUNT_NAME`: Where users pay you.
   - `YOUR_USDT_WALLET`: Your TRC20 address where users send USDT.
4. **Persistent Disk**: Go to **Disks** in Render and add a disk:
   - **Name**: `bot-data`
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: `1GB`

---

## 💻 How Users Trade

Users don't need to know commands; they can just talk to the bot in normal Pidgin!

- **"Buy" / "I wan buy"**: Starts the purchase flow. The bot will ask for the amount, ask for the wallet address **twice**, show payment details, and wait for a screenshot.
- **"Sell" / "I wan sell"**: Starts the selling flow. The bot will ask for the amount, ask for bank details **twice**, show your USDT wallet, and wait for the TXID.
- **"Rates" / "Price"**: Shows today's exchange rates.
- **"History" / "Orders"**: Shows the last 10 trades.
- **"Help" / "Admin"**: Shows support contact info.
- **"Cancel"**: Aborts the current trade.

---

## 👨‍💼 Admin Management

### Setting Rates
Type `/setrate <buy> <sell>` (e.g., `/setrate 1480 1520`).
- **I Buy (1480)**: What you pay users (Naira/USDT).
- **I Sell (1520)**: What users pay you (Naira/USDT).

### Approving Trades
When a user submits a trade, you get a notification with a button. 
- **For Buy**: Check your bank, if Naira is there, send USDT to the verified wallet address provided, then click **Approved**.
- **For Sell**: Check your wallet, if USDT is there, pay Naira to the verified bank details provided, then click **Approved**.

### Broadcasting
Use `/broadcast <your message>` to talk to all your customers at once.

---

## 🏗️ System Architecture

### stateless Transaction Engine
The bot uses a stateless design. It doesn't hold user funds. It simply collects and verifies the *intent* to trade, confirms the details twice, and hands it to the Admin for manual fulfillment.

### Weighted Random Responses
All outgoing messages are pulled from a library in `responses.py`. Every interaction has 10+ Nigerian Pidgin variations, making the bot feel like a real human trader.

---

## ⚙️ Configuration Details (`.env`)

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot API Key. |
| `ADMIN_ID` | Numeric ID of the owner. |
| `TRONGRID_API_KEY` | Key for verifying USDT transactions. |
| `YOUR_USDT_WALLET` | Your TRC20 receiving address. |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Bot won't start** | Check `.env` format and ensure `BOT_TOKEN` is correct. |
| **USDT not verifying** | Check `TRONGRID_API_KEY` and wait 1 minute for blockchain sync. |
| **Database error** | Ensure the `data/` folder exists and has write permissions. |
| **Not responding** | Restart the bot or check your internet/server connection. |

---

## 📊 Database Schema (SQLite)

- **Users**: Basic tracking of IDs.
- **Transactions**: History of all trades + `details` column for verified wallet/bank info.
- **Settings**: Persistent storage for rates and 90-day reminder schedule.

**Happy trading! 🚀**
