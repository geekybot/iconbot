from iconsdk.signed_transaction import SignedTransaction
from iconsdk.builder.transaction_builder import (
    TransactionBuilder,
    DeployTransactionBuilder,
    CallTransactionBuilder,
    MessageTransactionBuilder
)
from iconsdk.builder.call_builder import CallBuilder

from telegram.ext import CommandHandler
from pymongo import MongoClient
from iconsdk.wallet.wallet import KeyWallet
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.icon_service import IconService
import logging
import json
import codecs
import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
import subprocess
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater
from html import escape
import math

updater = Updater(token='750046409:AAHrfTwy8dCz-PXF1RuTpubmOfwoFYEUkN0')
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

icon_service = IconService(HTTPProvider("http://52.66.110.234:9000",3))
icon_irc2_address = "cx3f4c246971a87a7dc456f3e772fbbde52ec18de2"




# calculate default step cost


def get_default_step_cost(wallet_address: str):
    governance_address = "cx0000000000000000000000000000000000000001"
    _call = CallBuilder()\
        .from_(wallet_address)\
        .to(governance_address)\
        .method("getStepCosts")\
        .build()
    _result = icon_service.call(_call)
    default_step_cost = int(_result["default"], 0)
    return default_step_cost
# gets token name
def get_token_name(wallet_address: str):
    call = CallBuilder()\
        .from_(wallet_address)\
        .to(icon_irc2_address)\
        .method("name")\
        .build()
    return icon_service.call(call)

# Returns token symbol
def get_token_symbol(wallet_address: str):
    call = CallBuilder()\
        .from_(wallet_address)\
        .to(icon_irc2_address)\
        .method("symbol")\
        .build()
    return icon_service.call(call)
# Returns token symbol
def get_token_balance(wallet_address: str):
    params = {
        "_owner": wallet_address
    }
    call = CallBuilder()\
        .from_(wallet_address)\
        .to(icon_irc2_address)\
        .method("balanceOf")\
        .params(params)\
        .build()
    print(icon_service.call(call))
    return int(icon_service.call(call),0)


def irc2_transfer(from_wallet, to_address: str, value: float):
    params = {"_to": to_address, "_value": value}

    # Enters transaction information.
    call_transaction = CallTransactionBuilder()\
        .from_(from_wallet.get_address())\
        .to(icon_irc2_address) \
        .step_limit(get_default_step_cost(from_wallet.get_address())*2)\
        .nid(3) \
        .nonce(4) \
        .method("transfer")\
        .params(params)\
        .build()
    signed_transaction = SignedTransaction(call_transaction, from_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash

# mongodb setup
client = MongoClient('localhost', 27017)
db = client.icon_database
collection = db.telegramusers

def commands(bot, update):
    user = update.message.from_user.username
    bot.send_message(chat_id=update.message.chat_id, text="Initiating commands /tip & /withdraw have a specfic format,\n use them like so:" +
                     "\n \n Parameters: \n <user> = target user to tip \n <amount> = amount of reddcoin to utilise \n <address> = reddcoin address to withdraw to \n \n Tipping format: \n /tip <user> <amount> \n \n Withdrawing format: \n /withdraw <address> <amount>")

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="The following commands are at your disposal: /hi , /commands , /deposit , /tip , /withdraw , /price , /marketcap or /balance")

# TODO: deposit icon
def deposit(bot, update):
    user = update.message.from_user.username
    if user is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please set a telegram username in your profile settings!")
    else:
        address = "/usr/local/bin/reddcoind"
        result = subprocess.run(
            [address, "getaccountaddress", user], stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        bot.send_message(chat_id=update.message.chat_id,
                         text="@{0} your depositing address is: {1}".format(user, clean))

# TODO: tip
def tip(bot, update):
    user = update.message.from_user.username
    message = update.message.text
    args = message.split(" ")
    sender = collection.find_one({"telegramUserId": user})
    receiver = collection.find_one({"telegramUserId": args[1][1:]})
    amount = 0
    print(args)
    print(args[2])
    print(args[2].lower() == "icx")
    if user is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please set a telegram username in your profile settings!")
    elif sender is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please create an account to start tipping people")
    elif receiver is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please ask @{0} to join our channel and create account".format(args[1][1:]))
    
    else:
        if args[2].lower() == "icx":  
            try:
                amount = int(args[3])*(10**18)
            except:
                bot.send_message(chat_id=update.message.chat_id,
                                text="Amount should be a sane number!!!!!")
            PRIVATE_KEY_FOR_TEST = bytes.fromhex(sender["privateKey"])
            sender_wallet = KeyWallet.load(PRIVATE_KEY_FOR_TEST)
            balance = icon_service.get_balance(sender["address"])
            amount = int(args[3])*(10**18)
            if balance > amount:
                transaction = TransactionBuilder().from_(sender_wallet.get_address()).to(receiver["address"]).value(amount).nid(0x3).nonce(50).build()
                estimate_step = icon_service.estimate_step(transaction)
                step_limit = estimate_step + 10000
                signed_transaction = SignedTransaction(
                    transaction, sender_wallet, step_limit)
                tx_hash = icon_service.send_transaction(signed_transaction)
                bot.send_message(chat_id=update.message.chat_id,
                                    text="Transaction has been submitted with TX hash "+tx_hash)
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                    text="Insufficient Balance")
        elif args[2].lower() == "irc2":
            try:
                amount = int(args[3])*(10**18)
            except:
                bot.send_message(chat_id=update.message.chat_id,
                                text="Amount should be a sane number!!!!!")
            PRIVATE_KEY_FOR_TEST = bytes.fromhex(sender["privateKey"])
            sender_wallet = KeyWallet.load(PRIVATE_KEY_FOR_TEST)
            balance = get_token_balance(sender["address"])
            amount = int(args[3])*(10**18)
            if balance > amount:
                tx_hash = irc2_transfer(sender_wallet, receiver["address"], amount)
                bot.send_message(chat_id=update.message.chat_id,
                                    text="Transaction has been submitted with TX hash "+tx_hash)
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                    text="Insufficient Balance")
        else:
            bot.send_message(chat_id=update.message.chat_id,
                                    text="Please follow The format to send\nICX: /tip @username ICX value\nIRC2: /tip @username IRC2 value")

# TODO
def balance(bot, update):
    user = update.message.from_user.username
    sender = collection.find_one({"telegramUserId": user})
    if user is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please set a telegram username in your profile settings!")
    elif sender is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please create an account to start tipping people".format(args[1][1:]))
    else:
        balance_icx = round(icon_service.get_balance(sender["address"])*10**-18,3)
        balance_irc = round(get_token_balance(sender["address"])*10**-18,3)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Your Wallet Balance is\nICX: "+str(balance_icx)+"\nIRC2: "+str(balance_irc))

# TODO
def price(bot, update):
    quote_page = requests.get('https://www.worldcoinindex.com/coin/reddcoin')
    strainer = SoupStrainer('div', attrs={'class': 'row mob-coin-table'})
    soup = BeautifulSoup(quote_page.content,
                         'html.parser', parse_only=strainer)
    name_box = soup.find('div', attrs={'class': 'col-md-6 col-xs-6 coinprice'})
    name = name_box.text.replace("\n", "")
    price = re.sub(r'\n\s*\n', r'\n\n', name.strip(), flags=re.M)
    fiat = soup.find('span', attrs={'class': ''})
    kkz = fiat.text.replace("\n", "")
    percent = re.sub(r'\n\s*\n', r'\n\n', kkz.strip(), flags=re.M)
    quote_page = requests.get(
        'https://bittrex.com/api/v1.1/public/getticker?market=btc-rdd')
    soup = BeautifulSoup(quote_page.content, 'html.parser').text
    btc = soup[80:]
    sats = btc[:-2]
    bot.send_message(chat_id=update.message.chat_id,
                     text="Reddcoin is valued at {0} Δ {1} ≈ {2}".format(price, percent, sats) + " ฿")

# TODO
def withdraw(bot, update):
    user = update.message.from_user.username
    if user is None:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please set a telegram username in your profile settings!")
    else:
        target = update.message.text[9:]
        address = target[:35]
        address = ''.join(str(e) for e in address)
        target = target.replace(target[:35], '')
        amount = float(target)
        core = "/usr/local/bin/reddcoind"
        result = subprocess.run(
            [core, "getbalance", user], stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        balance = float(clean)
        if balance < amount:
            bot.send_message(chat_id=update.message.chat_id,
                             text="@{0} you have insufficent funds.".format(user))
        else:
            amount = str(amount)
            tx = subprocess.run(
                [core, "sendfrom", user, address, amount], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id,
                             text="@{0} has successfully withdrew to address: {1} of {2} RDD" .format(user, address, amount))

# Dummy
def hi(bot, update):
    user = update.message.from_user.username
    bot.send_message(chat_id=update.message.chat_id,
                     text="Hello @{0}, how are you doing today?".format(user))
    
# start command to create a wallet and map to user name
def start(bot, update):
    user = update.message.from_user.username
    tel_user = collection.find_one({"telegramUserId": user})
    print(update.message)
    print("==================")
    print(update.message.text)
    if tel_user is None:
        wallet = KeyWallet.create()
        pub_k = wallet.get_address()
        priv_k = wallet.get_private_key()
        account = {
            "telegramUserId": user,
            "privateKey": priv_k,
            "address": pub_k
        }
        collection.insert_one(account)
        bot.send_message(chat_id=update.message.chat_id, text="Hello @{0}, how are you doing today?".format(
            user)+"\nWe have set up you wallet, Your address is " + pub_k)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Hello @{0}, how are you doing today?".format(user))

# Dummy
def moon(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Moon mission inbound!")
    
# TODO
def marketcap(bot, update):
    quote_page = requests.get('https://www.worldcoinindex.com/coin/reddcoin')
    strainer = SoupStrainer('div', attrs={'class': 'row mob-coin-table'})
    soup = BeautifulSoup(quote_page.content,
                         'html.parser', parse_only=strainer)
    name_box = soup.find(
        'div', attrs={'class': 'col-md-6 col-xs-6 coin-marketcap'})
    name = name_box.text.replace("\n", "")
    mc = re.sub(r'\n\s*\n', r'\n\n', name.strip(), flags=re.M)
    bot.send_message(chat_id=update.message.chat_id,
                     text="The current market cap of Reddcoin is valued at {0}".format(mc))

commands_handler = CommandHandler('commands', commands)
dispatcher.add_handler(commands_handler)

moon_handler = CommandHandler('moon', moon)
dispatcher.add_handler(moon_handler)

hi_handler = CommandHandler('hi', hi)
dispatcher.add_handler(hi_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

withdraw_handler = CommandHandler('withdraw', withdraw)
dispatcher.add_handler(withdraw_handler)

marketcap_handler = CommandHandler('marketcap', marketcap)
dispatcher.add_handler(marketcap_handler)

deposit_handler = CommandHandler('deposit', deposit)
dispatcher.add_handler(deposit_handler)

price_handler = CommandHandler('price', price)
dispatcher.add_handler(price_handler)

tip_handler = CommandHandler('tip', tip)
dispatcher.add_handler(tip_handler)

balance_handler = CommandHandler('balance', balance)
dispatcher.add_handler(balance_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

updater.start_polling()

