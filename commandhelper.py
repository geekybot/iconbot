import mongodb as md
import iconactions as ica
from telethon.sync import TelegramClient
import asyncio
from telegram.ext.dispatcher import run_async
from telegram import  InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ParseMode
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
    if update.message.chat.type != "private":
        return
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
    if update.message.chat.type != "private":
        return
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
        amount_input = args[2]
        token = args[3]
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
        success_message = '{} tipped {} {} to {}, check '.format(user, amount_input, token, receiver_id )
        print(success_message)
        if token.lower() == "icx":
            tx_hash, message = ica.tip_icx(amount, sender, receiver["recAddress"])
            if tx_hash is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
                return
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text='{} <a href="https://bicon.tracker.solidwallet.io/transaction/{}">Here</a>'.format(success_message, tx_hash),
                    parse_mode=ParseMode.HTML
                )
                return
        elif token.lower() == "usd":
            price = float(str(ica.icx_usd())[:5])
            amount = int(amount/price)
            tx_hash, message = ica.tip_icx(amount, sender, receiver["recAddress"])
            if tx_hash is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
                return
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text='{} <a href="https://bicon.tracker.solidwallet.io/transaction/{}">Here</a>'.format(success_message, tx_hash),
                    parse_mode=ParseMode.HTML
                )
            return
        elif token.lower() == "irc2":
            tx_hash, message = ica.tip_irc(amount, sender, receiver["recAddress"])
            if tx_hash is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
                return
            else:
                context.bot.send_message(
                    chat_id=update.message.chat_id, text='{} <a href="https://bicon.tracker.solidwallet.io/transaction/{}">Here</a>'.format(success_message, tx_hash),
                    parse_mode=ParseMode.HTML
                )
                return
        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Please follow The format to send\nICX: /tip @username ICX value\nIRC2: /tip @username IRC2 value",
            )
            return


def balance(update, context):
    if update.message.chat.type != "private":
        return
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
    if update.message.chat.type != "private":
        return
    user = update.message.from_user.username
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=cb.price_callback(),
    )


def withdraw(update, context):
    if update.message.chat.type != "private":
        return
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
    if update.message.chat.type != "private":
        return
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
    if update.message.chat.type != "private":
        return
    print(update)
    user = update.message.from_user.username
    tel_user = md.find_one({"telegramUserId": user})
    keyboard = [[KeyboardButton("/help")],
                 [KeyboardButton("/wallet")],
                [KeyboardButton("/price")],
                 [KeyboardButton("/apps")]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    if tel_user is None:
        pub_k = ica.create_wallet(user)
    update.message.reply_text('Welcome to Pluttest, a telegram tipper Bot for Icon Blockchain:',
                               reply_markup=reply_markup)
   
# import new private key to delete created private key
def import_private_key(update, context):
    if update.message.chat.type != "private":
        return
    message = update.message.text
    args = message.split(" ")
    
    cb_dat = 'confirmpriv'
    print(type(cb_dat))
    # {'action':'confirm_priv', 'username': update.message.from_user.username, 'prik': args[1]}
    keyboard = [[InlineKeyboardButton("Confirm", callback_data= cb_dat),
                 InlineKeyboardButton("Cancel", callback_data='cancel_priv')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # result = md.import_pri_key(update.message.from_user.username, args[1])
    context.bot.send_message(
                chat_id=update.message.chat_id,
                text="This wallet might have balance, are you sure you want to continue?\n{}".format(args[1]),
                reply_markup = reply_markup
            )
# change receiving key 
def change_receiving_address(update, context):
    if update.message.chat.type != "private":
        return
    message = update.message.text
    args = message.split(" ")
    result = md.change_rec_address(update.message.from_user.username, args[1])
    context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Receiving address is changed to {}".format(args[1]),
            )
# reset wallet to change sending and receiving address as same
def reset_wallet(update, context):
    if update.message.chat.type != "private":
        return
    result = md.reset_wallet(update.message.from_user.username)
    context.bot.send_message(
                chat_id=update.message.chat_id,
                text="Wallet reset is completed",
            )
    
def button(update, context):
    query = update.callback_query
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
        # update.
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

    elif query.data == "confirmpriv":
        result = md.import_pri_key(query.from_user.username, query.message.text[-64:])
        query.edit_message_text(text="Success")
        context.bot.answer_callback_query(query.id)
    
    elif query.data == "cancel_priv":
        query.edit_message_text(text="Canceled")
        context.bot.answer_callback_query(query.id)
        
