from pymongo import MongoClient
from telethon import TelegramClient, sync
import asyncio
api_id = 1357005
api_hash = '9c4180ae436e5c5ea387a0209c101c87'
bot_token = '750046409:AAHrfTwy8dCz-PXF1RuTpubmOfwoFYEUkN0'
loop = asyncio.new_event_loop()
bot = TelegramClient('bot', api_id, api_hash,loop=loop).start(bot_token=bot_token)
group_username = 'bottesticon'
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


async def list_account(user):
    participants = await bot.get_participants(group_username)
    # print(participants)
    addresses = []
    participant1 = [p for p in participants if p.username != user]
    participant2 = [q for q in participant1 if q.username != 'pluttest_bot']
    # print(participant2)
    if len(participant2):
        for x in participant2:
            res = find_one({'telegramUserId': x.username})
            if res is not None:
                print(res)
                print(addresses)
                addresses.append(res['address'])
    return addresses

# print(list_account('Johnblockchain'))