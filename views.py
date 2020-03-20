BASE_START_TEXT = ("""
Hello {user_name}!. Welcome to TronBot
/help - Assistant to work with the bot
""")

TIPS_VIEW = ("""
Tipping members are as easy as ever
Reply to an user to tip
/tip {amount} {token}

Tip using uername 

/tip @{username} {token} {amount}
*token*: icx/irc2
*amount*: token amount to send         
""")

AIRDROP_VIEW = ("""
Airdrop users with you token
/airdrop {amount} {token}
*token*: icx/irc2
*amount*: token amount to airdrop         
""")

HELP_VIEW = ("""
@pluttest - Telegram bot that helps you with send, find data in Blockchain TRON
*Commands*:
/start - Start Bot
/price - Actual course
/balance {address} - Getting balance at
""")

PRICE_VIEW = ("""
*Price:* {price}
*Price BTC: * {price_btc}
*Global Rank:* {rank} 
*Market Cap:* {market_cap}
*24h Volume:* {volume_24h}
""")


ACCOUNTS_VIEW = ("""
*Address* {address}
*Balance TRX* {balance} 
---------------------
""")