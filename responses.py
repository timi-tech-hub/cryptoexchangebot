import random

RESPONSES = {
    "WELCOME": [
        "How far! 🏦 Welcome to the P2P Exchange. Ready to trade some USDT? Just type 'buy' or 'sell' make we start!",
        "Hello boss! 👋 Your P2P plug is here. You wan swap Naira for USDT or USDT for Naira? I dey ready.",
        "Welcome o! ⚡ Trading USDT here na sharp sharp. You wan check 'rates' or you wan start trade now?",
        "Greetings! 😊 I fit help you buy or sell USDT instantly. Wetin we dey trade today?",
        "How body? 🏦 Looking for fast and secure USDT/Naira exchange? You're in the right place, no wahala.",
        "Yo! Ready for some action? 🚀 Tell me if you wan buy or sell USDT make we move.",
        "Welcome! I dey here to make your crypto-to-cash trades smooth like butter. 💎 Type 'buy' or 'sell' when you ready.",
        "Hey! You need some USDT? Or you wan cash out to Naira? I've got you covered, boss. 🤝",
        "Hello! 🏦 This na your direct P2P link. No account, no stress. Wetin we dey swap today?",
        "How far! Let's get those trades moving. 📈 Type 'rates' to check market or jump straight into trade."
    ],
    "RATES_HEADER": [
        "No wahala! Here be today rates: 💱",
        "Checking market... 📉 Here's wetin we get for ground right now:",
        "Market update! 📊 See our current USDT/Naira prices:",
        "You wan see the prices? I get them here for you: 💰",
        "Here's the latest on our exchange rates, sharp sharp: 📈",
        "Current exchange prices don land! Check them out: 👇",
        "Always good to check rates first. Here they are: 💱",
        "Market dey move! 🚀 Check the current buy and sell prices:",
        "Looking for the best deal? Here be our rates for today: 💎",
        "Fresh rates just for you, boss! 📊 Take a look:"
    ],
    "BUY_START": [
        "Sharp! 🛒 How much USDT you wan buy today?",
        "Great choice. Abeg enter the amount of USDT you wan purchase:",
        "Make we get you some crypto! 🚀 How many USDT units you need?",
        "You ready to buy? Just tell me the USDT amount you want.",
        "Correct. Type the amount of USDT you're looking for:",
        "Cool! 🛒 How much USDT make I set aside for you?",
        "USDT coming right up. 💎 How many units we dey talk about?",
        "I fit help with that. Wetin be the USDT amount you need?",
        "Starting buy order... 📈 How much USDT you wan get?",
        "Nice! 🛒 Tell me the amount of USDT you wan buy."
    ],
    "BUY_AMOUNT_SUCCESS": [
        "Got it! {amount} USDT. ✅ Now, where I go send am? Abeg drop your TRC20 wallet address:",
        "Perfect. For {amount} USDT, I need your TRC20 wallet address to deliver the goods:",
        "Noted! {amount} USDT it is. 🎯 Wetin be your USDT (TRC20) wallet address?",
        "Confirmed: {amount} USDT. Abeg send me the wallet address where you wan receive am:",
        "Understood. {amount} USDT. ✅ Paste your TRC20 wallet address below:",
        "Sweet! {amount} USDT. 💎 Now, give me your USDT (TRC20) address make I know where to send am:",
        "Record set for {amount} USDT. 📝 Abeg provide your recipient wallet address (TRC20):",
        "Alright, {amount} USDT. 🎯 Where that crypto dey go? Send your wallet address:",
        "Confirmed. {amount} USDT units. ✅ I go need your TRC20 wallet address now:",
        "Okay! {amount} USDT. 🚀 Abeg send your USDT (TRC20) address below."
    ],
    "INVALID_AMOUNT": [
        "Oops! ❌ That one no be valid number. Abeg try again with just digits.",
        "Wait, I no get that one. 😅 Abeg enter a positive number for the amount.",
        "My bad, I need proper number make I move. ❌ Try type the amount again?",
        "That amount look somehow. ❌ Abeg use numbers only (e.g., 50).",
        "Sorry, I no fit process that one. ❌ Abeg enter valid numerical amount.",
        "Be like say typo dey! 😅 Abeg re-enter the amount using only numbers.",
        "Invalid input. ❌ I need positive number make I move forward. Try again?",
        "Hmm, something wrong. ❌ Abeg enter the amount in numbers.",
        "I need clear number for the trade. ❌ Abeg re-type the amount.",
        "Oops! ❌ Abeg enter valid number make we keep going."
    ],
    "BUY_WALLET_INVALID": [
        "Hmm, that one no look like standard TRC20 address. ❌ E suppose start with 'T' and be 34 characters. Try again?",
        "Wait! 🛑 TRC20 addresses usually start with 'T' and get 34 characters. Abeg double-check and re-send.",
        "That address no valid o. ❌ Make sure say na USDT TRC20 address starting with 'T'.",
        "I think mistake dey that wallet address. ❌ Abeg send valid 34-character TRC20 address.",
        "Whoops! ❌ That no be valid TRC20 address. Abeg check am and send am again.",
        "Double-check your wallet! 🛑 E need to be TRC20 address starting with 'T'.",
        "That one no match TRC20 format. ❌ Abeg provide correct address.",
        "I no fit send crypto to that one! 😅 Abeg provide valid USDT (TRC20) address.",
        "Invalid wallet detected. ❌ Abeg ensure say e start with 'T' and be 34 characters.",
        "Make we try that one again. ❌ Abeg send valid 34-character TRC20 wallet address."
    ],
    "BUY_WALLET_DOUBLE_CHECK": [
        "Just to be 100% safe... 🛡️ Abeg **RE-ENTER** that wallet address one more time:",
        "Safety first! ⚠️ Abeg **type your wallet address again** make we sure say e correct:",
        "I want make sure your crypto go the right place. 🎯 Abeg **confirm your address** by typing am again:",
        "Almost there! ⚠️ Abeg **re-type the address** make we check say no typo dey:",
        "Make we avoid stories, abeg **send the wallet address again** for confirmation:",
        "Better safe than sorry! 🛡️ Abeg **re-enter your TRC20 address** make I confirm:",
        "Make we double-verify that one. ⚠️ Abeg **type the address again**:",
        "Just double-checking... 🎯 Abeg **re-send your wallet address** to confirm say e correct:",
        "One last check! ⚠️ Abeg **re-enter your address** make everything perfect:",
        "I need you to **confirm the address** by typing am one more time. Safety first, boss! 🛡️"
    ],
    "WALLET_MISMATCH": [
        "Whoops! ❌ Those two addresses no match o. Make we start the wallet part again for safety.",
        "Mismatch detected! 🛑 The addresses no be the same. Abeg send your USDT (TRC20) address again:",
        "Oh no, they no match. ❌ Make we try once more. Send your wallet address:",
        "Wait, those ones different! 😅 For your security, make we try enter the wallet address again:",
        "Typo alert! ❌ The addresses no match up. Abeg re-enter your wallet address:",
        "I notice difference between the two. 🛑 Make we restart the wallet confirmation. Send your address:",
        "Mismatch! ❌ Safety na key. Abeg send your USDT (TRC20) address again:",
        "They no match! 😅 No wahala, just send the correct wallet address again:",
        "I see mismatch. 🛑 Make we dey careful. Abeg re-send your TRC20 wallet address:",
        "Oops, those no match. ❌ Make we try again. Wetin be your USDT (TRC20) wallet address?"
    ],
    "BUY_PAYMENT_DETAILS": [
        "E don set! Wallet confirmed. ✅ See your payment instructions here:\n\nTotal: *₦{naira:,.2f}*\nBank: *{bank}*\nAcc No: `{acc}`\nName: {name}\n\n📸 Send screenshot when you done!",
        "All set! ✅ To get your {amount} USDT, abeg transfer *₦{naira:,.2f}* to:\n\n🏦 *{bank}*\n📌 `{acc}`\n👤 {name}\n\nDrop the proof here once you done!",
        "Confirmed! 🎯 Abeg pay *₦{naira:,.2f}* to this account:\n\n{bank}\n`{acc}`\n{name}\n\n📸 Send me the receipt or screenshot after payment.",
        "Got it! ✅ Your total na *₦{naira:,.2f}*. Transfer to:\n\n🏦 {bank}\nAcc: `{acc}`\nName: {name}\n\nI dey wait for your payment proof! 📸",
        "Excellent. 💎 Transfer *₦{naira:,.2f}* to our bank account:\n\n{bank} | `{acc}` | {name}\n\nOnce you done, send screenshot of the transaction here. ✅",
        "Payment info ready! 🎯 Send *₦{naira:,.2f}* to:\n\n🏦 *{bank}*\n📌 `{acc}`\n👤 {name}\n\n📸 Abeg upload your proof of payment sharp sharp!",
        "Alright! ✅ Pay *₦{naira:,.2f}* into:\n\n{bank}\n`{acc}`\n{name}\n\nSend picture of the transfer record when you finish. 📸",
        "Ready to go. 🚀 Transfer *₦{naira:,.2f}* to:\n\n🏦 {bank} | `{acc}` | {name}\n\n📸 Just drop the screenshot here make I notify admin.",
        "Confirming your order! ✅ Abeg send *₦{naira:,.2f}* to:\n\n{bank} - `{acc}` - {name}\n\n📸 Send proof of payment make we release your USDT.",
        "Payment details: 💰\nAmount: *₦{naira:,.2f}*\nBank: {bank}\nAccount: `{acc}`\nName: {name}\n\n📸 Send screenshot or receipt when you don pay!"
    ],
    "BUY_ORDER_COMPLETE": [
        "Got it! ✅ I don notify admin. Your USDT go dey your way as soon as they verify payment. Thanks!",
        "Received! 📸 Admin dey check the proof now. Your crypto go soon land. Thank you for trading!",
        "Perfect. ✅ I don submit your proof. Once they verify am, your USDT go hit your wallet. Chill small!",
        "All good! 🚀 I don pass your payment proof to admin. USDT go dey sent once they confirm. Thanks!",
        "Payment proof submitted! ✅ We go verify and send your USDT sharp sharp. Stay tuned.",
        "Thanks for the proof! 📸 Admin don get notification. You go get your USDT shortly after verification.",
        "Order complete! ✅ I don send everything to admin. Your crypto dey come soon. Thank you!",
        "Verified submission! 🎯 I don notify the boss. Your USDT go dey sent once transfer confirm.",
        "Done! ✅ Payment proof received. We dey process your order now. Thanks for choosing us!",
        "Great! 🚀 Proof received. USDT go hit your wallet once admin confirm the Naira. Thanks!"
    ],
    "SELL_START": [
        "Awesome! 💰 How much USDT you wan sell?",
        "Ready to cash out? Enter the amount of USDT you wan sell:",
        "Make we get you some Naira! 🚀 How many USDT units you dey sell?",
        "You wan cash out? 💰 Just tell me the amount of USDT you wan sell.",
        "Sure thing. Type the amount of USDT you're selling today:",
        "Cool! 💰 How much USDT we dey swap for Naira?",
        "USDT to Naira... 💎 How many units we dey trade?",
        "I fit help with that. Wetin be the USDT amount you dey sell?",
        "Starting sell order... 📉 How much USDT you wan cash out?",
        "Nice! 💰 Tell me the amount of USDT you wan sell."
    ],
    "SELL_AMOUNT_SUCCESS": [
        "Got it! {amount} USDT. ✅ Now, where I go send your Naira? Abeg drop your Bank Details (Bank, Acc No, Name):",
        "Perfect. For {amount} USDT, I need your bank details make I pay you. Abeg send: Bank Name, Account No, and Name.",
        "Noted! {amount} USDT it is. 🎯 Wetin be your bank details for receiving payment?",
        "Confirmed: {amount} USDT. Abeg send me the bank details where you wan receive your Naira:",
        "Understood. {amount} USDT. ✅ Paste your bank info below (Bank, Acc Num, Name):",
        "Sweet! {amount} USDT. 💎 Now, give me your bank details make I know where to send the Naira:",
        "Record set for {amount} USDT. 📝 Abeg provide your bank information for the transfer:",
        "Alright, {amount} USDT. 🎯 Where that Naira dey go? Send your bank details:",
        "Confirmed. {amount} USDT units. ✅ I go need your bank account details now:",
        "Okay! {amount} USDT. 🚀 Abeg send your bank details (Bank, Account No, Account Name) below."
    ],
    "SELL_BANK_INVALID": [
        "Hmm, I no fit find 10-digit account number for your message. ❌ Abeg provide full details: Bank, Account Number, and Name.",
        "Wait! 🛑 I need 10-digit account number make I move. You fit send the full details again?",
        "I miss the account number o. ❌ Abeg make sure say you include your 10-digit bank account number.",
        "Invalid bank details. ❌ Abeg provide the Bank Name, 10-digit Account Number, and Account Name.",
        "Whoops! ❌ I need that 10-digit account number. Abeg re-send your bank details clearly.",
        "Double-check your info! 🛑 Abeg provide valid 10-digit account number for your message.",
        "I no fit detect proper account number. ❌ Abeg send your full bank details again.",
        "I need 10-digit account number for the transfer. 😅 Abeg provide your full bank details.",
        "Missing info! ❌ Abeg ensure say your message get 10-digit account number.",
        "Make we try that one again. ❌ Abeg send your Bank Name, 10-digit Account Number, and Account Name."
    ],
    "SELL_BANK_DOUBLE_CHECK": [
        "Just to be 100% safe... 🛡️ Abeg **RE-ENTER your 10-digit Account Number** one more time:",
        "Safety first! ⚠️ Abeg **type your account number again** make we sure say e perfectly correct:",
        "I want make sure the Naira go the right person. 🎯 Abeg **confirm your account number** by typing am again:",
        "Almost there! ⚠️ Abeg **re-type the account number** make we check say no typo dey:",
        "Make we avoid stories, abeg **send the account number again** for confirmation:",
        "Better safe than sorry! 🛡️ Abeg **re-enter your 10-digit account number** make I confirm:",
        "Make we double-verify that one. ⚠️ Abeg **type the account number again**:",
        "Just double-checking... 🎯 Abeg **re-send your account number** to confirm say e correct:",
        "One last check! ⚠️ Abeg **re-enter your account number** make everything perfect:",
        "I need you to **confirm the account number** by typing am one more time. Safety first, boss! 🛡️"
    ],
    "ACC_MISMATCH": [
        "Whoops! ❌ Those account numbers no match o. Make we start the bank info part again for safety.",
        "Mismatch detected! 🛑 The account numbers no be the same. Abeg send your bank details again:",
        "Oh no, they no match. ❌ Make we try once more. Send your bank details (Bank, Acc Num, Name):",
        "Wait, those ones different! 😅 For your security, make we try enter the bank info again:",
        "Typo alert! ❌ The account numbers no match up. Abeg re-enter your bank details:",
        "I notice difference between the two. 🛑 Make we restart the bank confirmation. Send your details:",
        "Mismatch! ❌ Safety na key. Abeg send your bank information again:",
        "They no match! 😅 No wahala, just send the correct bank details again:",
        "I see mismatch. 🛑 Make we dey careful. Abeg re-send your bank details:",
        "Oops, those no match. ❌ Make we try again. Wetin be your bank details?"
    ],
    "SELL_INSTRUCTIONS": [
        "E don set! Bank details confirmed. ✅ Now, abeg send *{amount} USDT* (TRC20) to our wallet:\n\n`{wallet}`\n\n🔗 Send the **TXID (Hash)** once you done!",
        "All set! ✅ To get your Naira, abeg transfer *{amount} USDT* (TRC20) to:\n\n📌 `{wallet}`\n\nDrop the **Transaction Hash (TXID)** here once you don send am! 🔗",
        "Confirmed! 🎯 Abeg send *{amount} USDT* to our TRC20 wallet address:\n\n`{wallet}`\n\n🔗 Paste the **TXID** here after you don make transfer.",
        "Got it! ✅ Abeg send the *{amount} USDT* to:\n\n📌 `{wallet}`\n\nI dey wait for your **Transaction Hash (TXID)**! 🔗",
        "Excellent. 💎 Send *{amount} USDT* to this TRC20 wallet:\n\n`{wallet}`\n\nOnce you done, paste the **TXID** here make we verify. ✅",
        "Wallet ready! 🎯 Send *{amount} USDT* (TRC20) to:\n\n📌 `{wallet}`\n\n🔗 Abeg provide the **TXID** sharp sharp after you send am!",
        "Alright! ✅ Send *{amount} USDT* into our wallet:\n\n`{wallet}`\n\nSend the **Transaction Hash** when you finish. 🔗",
        "Ready to go. 🚀 Transfer *{amount} USDT* to:\n\n📌 `{wallet}`\n\n🔗 Just drop the **TXID** here make I notify admin.",
        "Confirming your sell order! ✅ Abeg send *{amount} USDT* to:\n\n`{wallet}`\n\n🔗 Send the **TXID** make we verify and pay you.",
        "USDT Address: 💰\nAmount: *{amount} USDT*\nWallet: `{wallet}`\n\n🔗 Paste the **TXID** here once transfer is done!"
    ],
    "SELL_ORDER_COMPLETE": [
        "Got it! ✅ I don notify admin. Your Naira go dey sent as soon as they verify USDT transfer. Thanks!",
        "Received! 🔗 Admin dey verify the USDT now. You go get your payment sharp sharp. Thank you!",
        "Perfect. ✅ I don submit your TXID. Once verified, the Naira go hit your account. Chill small!",
        "All good! 🚀 I don pass your TXID to admin. You go get paid once they confirm. Thanks!",
        "Order submitted! ✅ We go verify the USDT and send your Naira sharp sharp. Stay tuned.",
        "Thanks for the TXID! 🔗 Admin don get notification. You go get your Naira shortly after verification.",
        "Order complete! ✅ I don send everything to admin. Your payment dey come soon. Thank you!",
        "Verified submission! 🎯 I don notify the boss. Your Naira go dey sent once USDT confirm.",
        "Done! ✅ TXID received. We dey process your payment now. Thanks for choosing us!",
        "Great! 🚀 TXID received. Naira go hit your account once admin confirm the USDT. Thanks!"
    ],
    "CANCEL_TRADE": [
        "❌ Trade cancelled. No wahala, we fit always try again later!",
        "Alright, I don cancel that for you. 👋 Let me know if you need anything else.",
        "Order aborted. ❌ Type 'buy' or 'sell' if you change your mind!",
        "Cancelled! 👋 I dey here if you wan start new trade.",
        "No wahala! ❌ I don stop the current process. See you around!",
        "Trade cancelled. 👋 Feel free to check 'rates' anytime!",
        "Okay, I dey cancel that now. ❌ Hit me up when you ready to trade again.",
        "Stopped! 🛑 The trade don cancel. Have a great day!",
        "Trade aborted. ❌ No crypto or cash move. Let's talk later!",
        "Cancelled. 👋 Just say 'hi' make I see wetin else I fit do for you."
    ],
    "HISTORY_EMPTY": [
        "E be like say you never make any trades yet! 😅 You wan start your first one?",
        "No transaction history found o. 📝 Make we get some trades for ground!",
        "Your history empty! 🤷‍♂️ Buy or sell some USDT make e show for here.",
        "Nothing to show here yet. 📝 Ready to make your first trade?",
        "Your trade history currently blank. 📉 You wan see today 'rates'?",
        "No trades yet! 😅 I dey ready when you ready. Type 'buy' or 'sell'.",
        "Everywhere cool for here... 🤷‍♂️ No recent transactions found.",
        "History clean! ✨ Start trade make e show for here.",
        "No records found. 📝 Tell me if you wan buy or sell USDT!",
        "Nothing here o. 🤷‍♂️ Type 'rates' make you see if today na good day for trade!"
    ],
    "SUPPORT": [
        "You need help? 📞 My human boss dey here: [Click to Message](tg://user?id={admin_id})",
        "Stuck? 😅 No wahala! You fit contact our support admin directly: [Message Admin](tg://user?id={admin_id})",
        "You get questions? 📞 Our admin go happy to help you! Reach out here: [Contact Support](tg://user?id={admin_id})",
        "If something no clear, chat with boss: [Admin Link](tg://user?id={admin_id}) 🤝",
        "Support na just one click away! 📞 Message our admin: [Click here](tg://user?id={admin_id})",
        "You need hand? 🤝 Contact our team here: [Support Admin](tg://user?id={admin_id})",
        "For any issues or manual verification, talk to admin: [Message here](tg://user?id={admin_id})",
        "We dey for you! 📞 If you need help, message: [Support](tg://user?id={admin_id})",
        "Something dey your mind? 🤝 Chat with admin directly: [Admin Contact](tg://user?id={admin_id})",
        "Help dey way! 📞 Click here make you message admin: [Support Link](tg://user?id={admin_id})"
    ],
    "REMINDER": [
        "👋 *Friendly Reminder*\n\nJust quick note say we still dey here for your *USDT/Naira* exchange needs!\n\n✅ Fast Payments\n✅ Secure P2P Trading\n✅ Best Rates\n\nType 'rates' make you see current prices!",
        "How far! 👋 Long time no see. Just reminding you say we still get best rates for USDT/Naira swaps. 💎 You ready to trade?",
        "Hello! 😊 Hope your day dey go well. Just heads up say we open for USDT trades as always. 📈 Check 'rates' anytime!",
        "Hi! 👋 You need cash out some USDT? Or you wan buy some for your next move? We ready for you! 🏦",
        "Greetings! 💎 Just keeping in touch. We still be the fastest way to swap USDT and Naira. Type 'buy' or 'sell' make we start!",
        "Yo! 🚀 Just dropping by to say we still dey do P2P crypto exchanges. Best rates for town! 💱",
        "How far! 👋 No forget say we be your reliable P2P crypto partner. 🤝 Check our latest 'rates' now!",
        "Hello! 😊 Just small reminder say you fit buy or sell USDT right here, sharp sharp. 🏦 No accounts needed!",
        "Hi! 📈 Crypto market dey move o! Just reminding you say we dey here for all your USDT/Naira needs. 👋",
        "How far! 👋 E don tey. Just letting you know say we still dey process trades fast and secure. 🚀 Ready when you are!"
    ],
    "ADMIN_APPROVE_USER": [
        "✅ *Order #{tx_id} Done!* \n\nI don see your payment and I don send your crypto sharp sharp. 🚀 Thank you for trading with us, boss!",
        "E don set! ✅ *Order #{tx_id} Completed.* \n\nYour Naira don land and I don fire the USDT go your wallet. 💎 Thanks for the patronage!",
        "Confirmed! 🎯 *Order #{tx_id} Success.* \n\nPayment verified and crypto sent. No wahala. Always here for you! 🤝",
        "✅ *Order #{tx_id}* don clear. \n\nI don deposit the currency for you. Thanks for using our P2P service! 🚀",
        "Sharp sharp! ✅ *Order #{tx_id}* finished. \n\nYour trade don verify and I don send the crypto. We move! 📈",
        "Done deal! 🤝 *Order #{tx_id}* complete. \n\nI don see the money and I don credit you. God bless your hustle! 💰",
        "✅ *Order #{tx_id}* verified. \n\nEverything set, crypto don land your wallet. Thanks for trading with the plug! 💎",
        "Confirmed boss! ✅ *Order #{tx_id}* is complete. \n\nI don see the alert and I don send the USDT. Catch you next time! 🚀",
        "✅ *Order #{tx_id}* successful. \n\nCurrency don dey your side now. Thanks for trusting us! 🤝",
        "All set! ✅ *Order #{tx_id}* finished. \n\nPayment confirmed, crypto sent. Sharp sharp delivery! ⚡"
    ],
    "ADMIN_REJECT_USER": [
        "❌ *Order #{tx_id}* \n\nHow far boss, I never see the money for my side o. Abeg check your bank or send the proof again make I see.",
        "Wait small... ❌ *Order #{tx_id}* \n\nI never get alert for this payment yet. Abeg re-verify say you send am correctly.",
        "❌ *Order #{tx_id} Issue* \n\nMoney never show for ground o. I dey wait make the alert enter. Abeg check am.",
        "Hmm, ❌ *Order #{tx_id}* \n\nAlert never land. Be like say delay dey or something wrong. Check your app well.",
        "❌ *Order #{tx_id}* \n\nBoss, I never see this one o. Abeg verify the transfer well before you send proof again.",
        "Issue with *Order #{tx_id}* ❌ \n\nPayment never reflect for my side. Abeg double check the details you use pay.",
        "❌ *Order #{tx_id}* \n\nI never see money yet. Maybe network delay, but I still dey wait. Check your side too.",
        "🛑 *Order #{tx_id}* \n\nAlert never show face. Abeg make you check the transaction status for your bank app.",
        "❌ *Order #{tx_id} Rejected* \n\nI never see the credit for my bank. Abeg contact support or check if transfer fail.",
        "Wait o! ❌ *Order #{tx_id}* \n\nMoney never enter. Abeg verify and try again later if e be network issue. 🛑"
    ]
}

def get_text(key, **kwargs):
    """Get a random variation of a response text"""
    if key not in RESPONSES:
        return f"Error: Key {key} not found."
    
    text = random.choice(RESPONSES[key])
    return text.format(**kwargs)
