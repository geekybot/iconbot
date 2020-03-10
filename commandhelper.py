import mongodb as md
import iconactions as ica
from telethon.sync import TelegramClient
import asyncio
from telegram.ext.dispatcher import run_async



def commands(bot, update):
    user = update.message.from_user.username
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Initiating commands /tip has a specfic format,\n use it like so:"
        + "\n \n Parameters: \n <user> = target user to tip \n <token type> = icx or irc2 \n <amount> = amount of token to utilise  \n \n Tipping format: \n /tip <user> <toke type> <amount> ",
    )

@run_async
def airdrop(bot, update):
    user = update.message.from_user.username
    message = update.message.text
    args = message.split(" ")
    print(args)
    sender = md.find_one({"telegramUserId": user})
    try:
        amount = int(args[1]) * (10 ** 18)
    except:
        bot.send_message(
            chat_id=update.message.chat_id, text="Amount should be a sane number!!!!!",
        )
    token = args[2].lower()
    print(amount)
    print(sender)
    print(token)
    print(user)
    # tx_hash_list, error_list, message =
    ica.airdrop(amount, sender, token, user)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Airdrop Successful for: "
        # + str(tx_hash_list)
        + "\nFailed Tx: "
        # + str(error_list)
        + "\n"
        # + message,
    )
    # except:
    #     bot.send_message(
    #         chat_id=update.message.chat_id, text="Encountered an  error!!!!!",
    #     )


# get private keys
# def get_keys(bot, update):
#     group = update.message.chat.type == "group"
#     if group:
#         bot.send_message(
#             chat_id=update.message.chat_id,
#             text="Please ask for private keys from a private chat",
#         )
#     else:
#         private_key, address, message = ica.get_keys(
#             update.message.from_user.username
#         )
#         if private_key is None:
#             bot.send_message(chat_id=update.message.chat_id, text=message)
#         else:
#             bot.send_message(
#                 chat_id=update.message.chat_id,
#                 text="Public Address: \n" + address + "\nPrivate Key: \n" + private_key,
#             )


def help(bot, update):
    print(update)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="The following commands are at your disposal: /start , /hi , /commands , /tip, /balance",
    )


# TODO: deposit icon
def deposit(bot, update):
    group = update.message.chat.type == "group"
    if group:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Please ask for deposit address from private chat",
        )
    else:
        private_key, address, message = ica.get_keys(update.message.from_user.username)
        if private_key is None:
            bot.send_message(chat_id=update.message.chat_id, text=message)
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Your Deposit Address is: \n" + address,
            )


def tip(bot, update):
    user = update.message.from_user.username
    message = update.message.text
    args = message.split(" ")
    sender = md.find_one({"telegramUserId": user})
    receiver = md.find_one({"telegramUserId": args[1][1:]})
    amount = 0
    if user is None:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Please set a telegram username in your profile settings!",
        )
    elif sender is None:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Please create an account to start tipping people",
        )
    elif receiver is None:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Please ask @{0} to join our channel and create account".format(
                args[1][1:]
            ),
        )
    try:
        amount = int(args[3]) * (10 ** 18)
    except:
        bot.send_message(
            chat_id=update.message.chat_id, text="Amount should be a sane number!!!!!",
        )
    else:
        if args[2].lower() == "icx":
            tx_hash, message = ica.tip_icx(amount, sender, receiver["address"])
            if tx_hash is None:
                bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
            else:
                bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
        elif args[2].lower() == "irc2":
            tx_hash, message = ica.tip_irc(amount, sender, receiver["address"])
            if tx_hash is None:
                bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
            else:
                bot.send_message(
                    chat_id=update.message.chat_id, text=message,
                )
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Please follow The format to send\nICX: /tip @username ICX value\nIRC2: /tip @username IRC2 value",
            )


def balance(bot, update):
    user = update.message.from_user.username
    if user is None:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Please set a telegram username in your profile settings!",
        )
    else:
        sender, balance_icx, balance_irc = ica.get_balance_user(user)
        if not sender:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Please create an account to start tipping people".format(
                    args[1][1:]
                ),
            )
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Your Wallet Balance is\nICX: "
                + str(balance_icx)
                + "\nIRC2: "
                + str(balance_irc),
            )


# TODO
def price(bot, update):
    user = update.message.from_user.username


# TODO
def withdraw(bot, update):
    user = update.message.from_user.username


# Dummy
def hi(bot, update):
    user = update.message.from_user.username
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello @{0}, how are you doing today?".format(user),
    )


# start command to create a wallet and map to user name
def start(bot, update):
    user = update.message.from_user.username
    tel_user = md.find_one({"telegramUserId": user})
    if tel_user is None:
        pub_k = ica.create_wallet(user)
        # print(response)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Hello @{0}, how are you doing today?".format(user)
            + "\nWe have set up you wallet, Your address is "
            + pub_k,
        )
    else:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Hello @{0}, how are you doing today?".format(user),
        )
