from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater
import math
import config as cfg
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

updater = Updater(token=cfg.config["bot_token"])
dispatcher = updater.dispatcher

import commandhelper as ch

commands_handler = CommandHandler("commands", ch.commands)
dispatcher.add_handler(commands_handler)

hi_handler = CommandHandler("hi", ch.hi)
dispatcher.add_handler(hi_handler)

start_handler = CommandHandler("start", ch.start)
dispatcher.add_handler(start_handler)

deposit_handler = CommandHandler("deposit", ch.deposit)
dispatcher.add_handler(deposit_handler)

price_handler = CommandHandler("price", ch.price)
dispatcher.add_handler(price_handler)

tip_handler = CommandHandler("tip", ch.tip)
dispatcher.add_handler(tip_handler)

balance_handler = CommandHandler("balance", ch.balance)
dispatcher.add_handler(balance_handler)

help_handler = CommandHandler("help", ch.help)
dispatcher.add_handler(help_handler)

airdrop_handler = CommandHandler("airdrop", ch.airdrop)
dispatcher.add_handler(airdrop_handler)

export_handler = CommandHandler("export", ch.get_keys)
dispatcher.add_handler(export_handler)

withdraw_handler = CommandHandler("withdraw", ch.withdraw)
dispatcher.add_handler(withdraw_handler)

updater.start_polling()
# updater.idle()
