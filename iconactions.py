from iconsdk.signed_transaction import SignedTransaction
from iconsdk.builder.transaction_builder import (
    TransactionBuilder,
    DeployTransactionBuilder,
    CallTransactionBuilder,
    MessageTransactionBuilder,
)
from iconsdk.builder.call_builder import CallBuilder

from iconsdk.wallet.wallet import KeyWallet
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.icon_service import IconService
import mongodb as md
import math  


import asyncio

# icon_service = IconService(HTTPProvider("http://52.66.xx.xx:9000",3))
icon_service = IconService(HTTPProvider("https://bicon.net.solidwallet.io/api/v3"))
# icon_irc2_address = "cx3f4c246971a87a7dc456f3e772fbbde52ec18de2"
icon_irc2_address = "cxe9f4d7d376811bf5d773789134e6a862009bd39c"


# Create Wallet for new users
def create_wallet(user_id):
    wallet = KeyWallet.create()
    pub_k = wallet.get_address()
    priv_k = wallet.get_private_key()
    account = {"telegramUserId": user_id, "privateKey": priv_k, "address": pub_k}
    response = md.insert_one(account)
    print("=================")
    print(response)
    return pub_k


# get balance of an user
def get_balance_user(user):
    try:
        sender = md.find_one({"telegramUserId": user})
        if sender is None:
            return False, 0, 0
        balance_icx = round(icon_service.get_balance(sender["address"]) * 10 ** -18, 3)
        balance_irc = round(get_token_balance(sender["address"]) * 10 ** -18, 3)
        return True, balance_icx, balance_irc
    except:
        return False, 0, 0


# calculate default step cost
def get_default_step_cost(wallet_address: str):
    governance_address = "cx0000000000000000000000000000000000000001"
    _call = (
        CallBuilder()
        .from_(wallet_address)
        .to(governance_address)
        .method("getStepCosts")
        .build()
    )
    _result = icon_service.call(_call)
    default_step_cost = int(_result["default"], 0)
    return default_step_cost


# gets token name
def get_token_name(wallet_address: str):
    call = (
        CallBuilder().from_(wallet_address).to(icon_irc2_address).method("name").build()
    )
    return icon_service.call(call)


# Returns token symbol
def get_token_symbol(wallet_address: str):
    call = (
        CallBuilder()
        .from_(wallet_address)
        .to(icon_irc2_address)
        .method("symbol")
        .build()
    )
    return icon_service.call(call)


# Returns token symbol
def get_token_balance(wallet_address: str):
    params = {"_owner": wallet_address}
    call = (
        CallBuilder()
        .from_(wallet_address)
        .to(icon_irc2_address)
        .method("balanceOf")
        .params(params)
        .build()
    )
    print(icon_service.call(call))
    return int(icon_service.call(call), 0)


def irc2_transfer(from_wallet, to_address: str, value: float):
    params = {"_to": to_address, "_value": value}

    # Enters transaction information.
    call_transaction = (
        CallTransactionBuilder()
        .from_(from_wallet.get_address())
        .to(icon_irc2_address)
        .step_limit(get_default_step_cost(from_wallet.get_address()) * 2)
        .nid(3)
        .nonce(4)
        .method("transfer")
        .params(params)
        .build()
    )
    signed_transaction = SignedTransaction(call_transaction, from_wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)
    return tx_hash


def tip_icx(amount, sender, receiver):
    try:
        PRIVATE_KEY_FOR_TEST = bytes.fromhex(sender["privateKey"])
        sender_wallet = KeyWallet.load(PRIVATE_KEY_FOR_TEST)
        balance = icon_service.get_balance(sender["address"])
        if balance >= amount:
            transaction = (
                TransactionBuilder()
                .from_(sender_wallet.get_address())
                .to(receiver)
                .value(amount)
                .nid(0x3)
                .nonce(50)
                .build()
            )
            estimate_step = 180000
            step_limit = estimate_step + 10000
            signed_transaction = SignedTransaction(
                transaction, sender_wallet, step_limit
            )
            tx_hash = icon_service.send_transaction(signed_transaction)
            return tx_hash, "Transaction has been submitted with TX hash " + tx_hash
        else:
            return None, "Error Submitting Transaction"
    except:
        return None, "Insufficient Balance"


#  tip irc
def tip_irc(amount, sender, receiver):
    try:
        PRIVATE_KEY_FOR_TEST = bytes.fromhex(sender["privateKey"])
        sender_wallet = KeyWallet.load(PRIVATE_KEY_FOR_TEST)
        balance = get_token_balance(sender["address"])
        if balance >= amount:
            tx_hash = irc2_transfer(sender_wallet, receiver, amount)
            return tx_hash, "Transaction has been submitted with TX hash " + tx_hash
        else:
            return None, "Error Submitting Transaction"
    except:
        return None, "Insufficient Balance"


#  get private keys
def get_keys(user):
    try:
        User = md.find_one({"telegramUserId": user})
        priv_key = User["privateKey"]
        address = User["address"]
        if User is not None:
            return priv_key, address, None
        else:
            return None, None, "Please use command /start to go"
    except:
        return None, None, "An error occurred"


def airdrop(bot, update, amount, sender, token, user, loop):
    
    try:
        PRIVATE_KEY_FOR_TEST = bytes.fromhex(sender["privateKey"])
        sender_wallet = KeyWallet.load(PRIVATE_KEY_FOR_TEST)
        if update.message.chat.username is None:
            bot.send_message(
            chat_id=update.message.chat_id,
            text= "Please st a group username to airdrop"
        )
        
        # loop = asyncio.get_event_loop()
        addresses = md.list_account(user, update.message.chat.username, loop)
        print("==================printing addresses======================")
        print(addresses)
        user_amount = int(amount / len(addresses))
        print(user_amount/10**18)
        # print(type(user_amount))
        message = "Airdrop\n"
        for x in addresses:
            message = message + "\n@"+ x["username"] + ": "+str(round(user_amount* (10 ** -18),3))
        print(message)
        bot.send_message(
            chat_id=update.message.chat_id,
            text= message
        )
        tx_hash_list = []
        error_list = []
        print("=================")
        print(token)
        if token == "icx":
            try:
                balance = icon_service.get_balance(sender["address"])
                if balance >= amount:
                    for x in addresses:
                        transaction = (
                            TransactionBuilder()
                            .from_(sender_wallet.get_address())
                            .to(x["address"])
                            .value(user_amount)
                            .nid(0x3)
                            .nonce(50)
                            .build()
                        )
                        estimate_step = 180000
                        step_limit = estimate_step + 10000
                        signed_transaction = SignedTransaction(
                            transaction, sender_wallet, step_limit
                        )
                        try:
                            tx_hash = icon_service.send_transaction(signed_transaction)
                            tx_hash_list.append(tx_hash)
                        except:
                            error_list.append(x)
                    return (
                        tx_hash_list,
                        error_list,
                        "Transaction has been submitted with TX hash ",
                    )
                else:
                    return None, None, "Insufficient balance"
            except:
                pass
        elif token == "irc2":
            print("Airdropping irc2")
            try:
                balance = get_token_balance(sender["address"])
                if balance >= amount:
                    for x in addresses:
                        try:
                            tx_hash = irc2_transfer(sender_wallet, x["address"], user_amount)
                            tx_hash_list.append(tx_hash)
                            print(tx_hash)
                        except:
                            error_list.append(x)
                    return (
                        tx_hash_list,
                        error_list,
                        "Transaction has been submitted with TX hash ",
                    )
                else:
                    return None, None, "Insufficient balance"
            except:
                pass
    except:
        return None, None, "Error Submitting Transactions"

# def test():
#     print(md.list_account('Johnblockchain'))
    
# test()