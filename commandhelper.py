import mongodb as md
import iconactions as ica
from telethon.sync import TelegramClient
import asyncio
from telegram.ext.dispatcher import run_async
from telegram import  InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import threading
import json
import callbacks as cb
import views

def commands(update, context):
    user = update.message.from_user.username
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Initiating commands /tip has a specfic format,\n use it like so:"
        + "\n \n Parameters: \n <user> = target user to tip \n <token type> = icx or irc2 \n <amount> = amount of token to utilise  \n \n Tipping format: \n /tip <user> <toke type> <amount> ",
    )

# @run_async
def airdrop(update, context):
    user = update.message.from_user.username
    message = update.message.text
    args = message.split(" ")
    print(args)
    sender = md.find_one({"telegramUserId": user})
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # addresses = md.list_account('Johnblockchain', loop)
    
    print("printing at commandhandler"+ update.message.chat.type)
    if update.message.chat.type == "private":
        print("in private")
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text= 'Airdrop only works in a group'
        )
        return
    # print(addresses)
    try:
        amount = int(float(args[1]) * (10 ** 18))
    except:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Amount should be a sane number!!!!!",
        )
        return
    token = args[2].lower()
    context.bot.send_message(
            chat_id=update.message.chat_id, text="Airdrop in process!!!!!",
        )
    ica.airdrop(context.bot, update, amount, sender, token, user, loop)
    

# get private keys
def get_keys(update, context):
    print(update.message.chat)
    group = update.message.chat.type != "private"
    if group:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please ask for private keys from a private chat",
        )
        
    else:
        private_key, address, message = ica.get_keys(
            update.message.from_user.username
        )
        if private_key is None:
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Public Address: \n" + address + "\nPrivate Key: \n" + private_key,
            )


def help(update, context):
    keyboard = [[InlineKeyboardButton("Tipping", callback_data='tipping'),
                 InlineKeyboardButton("Airdrop", callback_data='airdrop')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # query.edit_message_text(text=views.HELP_VIEW, reply_markup = reply_markup)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=cb.help_callback(),
        reply_markup = reply_markup
    )


# TODO: deposit icon
def deposit(update, context):
    group = update.message.chat.type == "group"
    if group:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please ask for deposit address from private chat",
        )
        return
    else:
        private_key, address, message = ica.get_keys(update.message.from_user.username)
        if private_key is None:
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Your Deposit Address is: \n" + address,
            )


def tip(update, context):
    user = update.message.from_user.username
    message = update.message.text
    args = message.split(" ")
    sender = md.find_one({"telegramUserId": user})
    try:
        print("=======tip=======")
        print(update.message.reply_to_message.from_user.is_bot)
        if update.message.reply_to_message.from_user.is_bot:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="You can't tip a bot!!",
            )
            return
        receiver_id = update.message.reply_to_message.from_user.username
        token = args[2]
        amount_input = args[1]
    except:
        receiver_id = args[1][1:]
        token = args[2]
        amount_input = args[3]
    receiver = md.find_one({"telegramUserId": receiver_id})
    amount = 0
    print("=======tip=======")
    print(receiver_id)
    if user is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please set a telegram username in your profile settings!",
        )
        return
    elif sender is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please create an account to start tipping people",
        )
        return
    elif receiver is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please ask @{0} to join our channel and create account".format(
                receiver_id
            ),
        )
        return
    try:
        amount = int(float(amount_input) * (10 ** 18))
        print(amount)
    except:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Amount should be a sane number!!!!!",
        )
        return
    else:
        if token.lower() == "icx":
            tx_hash, message = ica.tip_icx(amount, sender, receiver["address"])
            if tx_hash is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
                return
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
                return
        elif token.lower() == "irc2":
            tx_hash, message = ica.tip_irc(amount, sender, receiver["address"])
            if tx_hash is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
                return
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
                return
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Please follow The format to send\nICX: /tip @username ICX value\nIRC2: /tip @username IRC2 value",
            )
            return


def balance(update, context):
    user = update.message.from_user.username
    if user is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please set a telegram username in your profile settings!",
        )
        return
    else:
        sender, balance_icx, balance_irc = ica.get_balance_user(user)
        if not sender:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Please create an account to start tipping people".format(
                    args[1][1:]
                ),
            )
            return
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Your Wallet Balance is\nICX: "
                + str(balance_icx)
                + "\nIRC2: "
                + str(balance_irc),
            )
            return


# TODO
def price(update, context):
    user = update.message.from_user.username



def withdraw(update, context):
    user = update.message.from_user.username
    message = update.message.text
    args = message.split(" ")
    sender = md.find_one({"telegramUserId": user})
    receiver = args[3]
    amount = 0
    if user is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please set a telegram username in your profile settings!!",
        )
    elif sender is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Please create an account to start tipping people",
        )
    try:
        amount = int(float(args[1]) * (10 ** 18))
        print(amount)
    except:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Amount should be a sane number!!!!!",
        )
    else:
        if args[2].lower() == "icx":
            tx_hash, message = ica.tip_icx(amount, sender, receiver)
            if tx_hash is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
        elif args[2].lower() == "irc2":
            tx_hash, message = ica.tip_irc(amount, sender, receiver)
            if tx_hash is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Please follow The format to withdraw\nICX: /withdraw <value> ICX <address>\nIRC2: /withdraw <value> ICX <address>",
            )


# Dummy
def wallet(update, context):
    user = update.message.from_user.username
    keyboard = [[InlineKeyboardButton("Address", callback_data='address'),
                 InlineKeyboardButton("Balance", callback_data='balance'),
                 InlineKeyboardButton("Private Key", callback_data='private_key')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Wallet Information",
        reply_markup = reply_markup
    )



# start command to create a wallet and map to user name
def start(update, context):  
    keyboard = [[KeyboardButton("/help")],
                 [KeyboardButton("/wallet")],
                [KeyboardButton("/price")],
                 [KeyboardButton("/apps")]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to Pluttest, a telegram tipper Bot for Icon Blockchain:',
                               reply_markup=reply_markup)
   

    
def button(update, context):
    query = update.callback_query
    print(update)
    if query.data == 'help':
        keyboard = [[InlineKeyboardButton("Tipping", callback_data='tipping'),
                 InlineKeyboardButton("Airdrop", callback_data='airdrop')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=views.HELP_VIEW, reply_markup = reply_markup)
        context.bot.answer_callback_query(query.id)
        
    elif query.data == 'wallet':
        keyboard = [[InlineKeyboardButton("Address", callback_data='address'),
                 InlineKeyboardButton("Balance", callback_data='balance'),
                 InlineKeyboardButton("Private Key", callback_data='private_key')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="""
                                This is a icon blockchain wallet 
                                You can use the following commands
                                /test1 - to do some stuff
                                /test2 - to do some other stuffs
                                """, reply_markup = reply_markup)
        context.bot.answer_callback_query(query.id)
    elif query.data == 'balance':
        print("====looking for update=====")
        print(query.message)
        keyboard = [[InlineKeyboardButton("Address", callback_data='address'),
                 InlineKeyboardButton("Balance", callback_data='balance'),
                 InlineKeyboardButton("Private Key", callback_data='private_key')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Fetching Your balance\nThis may take some time", reply_markup = reply_markup)
        query.edit_message_text(text=cb.balance_callback(query.message.chat.username), reply_markup = reply_markup)
        context.bot.answer_callback_query(query.id)
        
    elif query.data == 'address':
        keyboard = [[InlineKeyboardButton("Address", callback_data='address'),
                 InlineKeyboardButton("Balance", callback_data='balance'),
                 InlineKeyboardButton("Private Key", callback_data='private_key')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=cb.address_callback(query.message.chat.username), reply_markup = reply_markup)
        context.bot.answer_callback_query(query.id)
        
    elif query.data == 'private_key':
        print(update)
        keyboard = [[InlineKeyboardButton("Address", callback_data='address'),
                 InlineKeyboardButton("Balance", callback_data='balance'),
                 InlineKeyboardButton("Private Key", callback_data='private_key')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=cb.pk_callback(query.message.chat.username), reply_markup = reply_markup)
        context.bot.answer_callback_query(query.id)
        
    elif query.data == 'price':
        query.edit_message_text(text=cb.price_callback())
        context.bot.answer_callback_query(query.id)
        
    elif query.data == 'apps':
        query.edit_message_text(text=cb.apps_callback())
        context.bot.answer_callback_query(query.id)
        
    elif query.data == 'tipping':
        keyboard = [[InlineKeyboardButton("Tipping", callback_data='tipping'),
                 InlineKeyboardButton("Airdrop", callback_data='airdrop')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=views.TIPS_VIEW, reply_markup = reply_markup)
        context.bot.answer_callback_query(query.id)
        
    elif query.data == 'airdrop':
        keyboard = [[InlineKeyboardButton("Tipping", callback_data='tipping'),
                 InlineKeyboardButton("Airdrop", callback_data='airdrop')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=views.AIRDROP_VIEW, reply_markup = reply_markup)
        context.bot.answer_callback_query(query.id)
# user = update.message.from_user.username
# tel_user = md.find_one({"telegramUserId": user})
# if tel_user is None:
#     pub_k = ica.create_wallet(user)
#     # print(response)
#     context.bot.send_message(
#         chat_id=update.message.chat_id,
#         text="Hello @{0}, how are you doing today?".format(user)
#         + "\nWe have set up you wallet, Your address is "
#         + pub_k,
#     )
# else:
#     context.bot.send_message(
#         chat_id=update.message.chat_id,
#         text="Hello @{0}, how are you doing today?".format(user),
#     )
