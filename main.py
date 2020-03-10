from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater
import math

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token='750046409:AAHrfTwy8dCz-PXF1RuTpubmOfwoFYEUkN0')
dispatcher = updater.dispatcher

import commandhelper as ch

commands_handler = CommandHandler('commands', ch.commands)
dispatcher.add_handler(commands_handler)

hi_handler = CommandHandler('hi', ch.hi)
dispatcher.add_handler(hi_handler)

start_handler = CommandHandler('start', ch.start)
dispatcher.add_handler(start_handler)

deposit_handler = CommandHandler('deposit', ch.deposit)
dispatcher.add_handler(deposit_handler)

price_handler = CommandHandler('price', ch.price)
dispatcher.add_handler(price_handler)

tip_handler = CommandHandler('tip', ch.tip)
dispatcher.add_handler(tip_handler)

balance_handler = CommandHandler('balance', ch.balance)
dispatcher.add_handler(balance_handler)

help_handler = CommandHandler('help', ch.help)
dispatcher.add_handler(help_handler)

airdrop_handler = CommandHandler('airdrop', ch.airdrop)
dispatcher.add_handler(airdrop_handler)

updater.start_polling()
# updater.idle()
