from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest, ForwardMessagesRequest
from telethon.tl.types import PeerChannel, InputPeerSelf
from datetime import datetime, timedelta

# Replace these with your own values
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone = 'YOUR_PHONE_NUMBER'
group_username = 'GROUP_USERNAME'  # The username of the group
saved_message_id = 12345  # The ID of the message in your saved messages

client = TelegramClient(phone, api_id, api_hash)

async def find_active_members(group_username, days=30):
    group = await client.get_entity(group_username)
    offset_id = 0
    limit = 100
    active_members = []

    while True:
        history = await client(GetHistoryRequest(
            peer=PeerChannel(group.id),
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            if message.date > datetime.now() - timedelta(days=days):
                if message.sender_id not in active_members:
                    active_members.append(message.sender_id)
        offset_id = messages[-1].id

    return active_members

async def send_message_to_members(members, message):
    for user_id in members:
        user = await client.get_entity(user_id)
        await client.send_message(user, message)

async def forward_message_to_members(members, saved_message_id):
    for user_id in members:
        await client(ForwardMessagesRequest(
            from_peer=InputPeerSelf(),
            id=[saved_message_id],
            to_peer=user_id
        ))

async def main():
    await client.start()
    active_members = await find_active_members(group_username)
    await send_message_to_members(active_members, 'Hello! This is a private message.')
    await forward_message_to_members(active_members, saved_message_id)

with client:
    client.loop.run_until_complete(main())
