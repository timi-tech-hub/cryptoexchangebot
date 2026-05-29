#!/bin/bash
# CryptoSwap Bot - Startup script for Render/Linux
set -e  # Exit on error

echo "🚀 Starting CryptoSwap Bot on Render..."

# Install dependencies (Render usually does this automatically via requirements.txt, 
# but this is a backup)
pip install -r requirements.txt

# Run bot
echo "✅ Bot is starting..."
python bot.py
