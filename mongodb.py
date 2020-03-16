from pymongo import MongoClient
from telethon import TelegramClient, sync
import asyncio
import time
from iconsdk.wallet.wallet import KeyWallet

import config as cfg
api_id = cfg.config["api_id"]
api_hash = cfg.config["api_hash"]
bot_token = cfg.config["bot_token"]

client = MongoClient('localhost', 27017)
db = client.icon_database
collection = db.telegramusers

def find_one(query):
    query_result = collection.find_one(query)
    return query_result


def insert_one(new_obj):
    result = collection.insert_one(new_obj)
    print(result)
    return result


def list_account(user, group_name, loop):
    group_username = group_name
    ms = time.time()*1000.0
    botid = "bot_test"+str(int(ms))
    bot = TelegramClient(botid, api_id, api_hash, loop = loop).start(bot_token=bot_token)    
    # with bot:
    participants = bot.get_participants(group_username)
    print(participants)
    addresses = []
    participant1 = [p for p in participants if p.username != user]
    participant2 = [q for q in participant1 if q.username != 'pluttest_bot']
    # print(participant2)
    if len(participant2):
        for x in participant2:
            temp = {}
            res = find_one({'telegramUserId': x.username})
            if res is not None:
                temp['username'] = x.username
                temp["address"] = res["address"]
                addresses.append(temp)
            else:
                wallet = KeyWallet.create()
                pub_k = wallet.get_address()
                priv_k = wallet.get_private_key()
                account = {"telegramUserId": x.username, "privateKey": priv_k, "address": pub_k}
                print(account)
                collection.insert_one(account)
                temp['username'] = x.username
                temp["address"] = pub_k
                addresses.append(temp)
    return addresses

# print(list_account('Johnblockchain'))