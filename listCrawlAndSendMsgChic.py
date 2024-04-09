import asyncio
import aiofiles
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, UserNotMutualContactError
from telethon.tl.types import InputPeerUser
from tqdm import tqdm
import random
import json


crawl_api_id = '27312057'
crawl_api_hash = '0e9aeb04cbce227238a0faaeabec3341'
crawl_phone = '+85260245331'

send_api_id = '23688237'
send_api_hash = 'b4c894b6ad4e7c8b813b22a56871aee9'
send_phone = '+85261404506'

async def crawl_participants(crawl_client, group_link):
    participants = await crawl_client.get_participants(group_link)
    user_info = []

    for p in participants:
        user_info.append({
            'id': p.id,
            'username': p.username,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'access_hash': p.access_hash
        })
        await asyncio.sleep(0.3)

    async with aiofiles.open('user_info.json', 'w') as f:
        await f.write(json.dumps(user_info, indent=4))

    print("Participant information serialized to 'user_info.json'.")

async def load_user_info():
    async with aiofiles.open('user_info.json', 'r') as f:
        return json.loads(await f.read())

async def get_saved_message_ids(client):
    saved_messages = await client.get_messages('me', limit=None)
    message_ids = [msg.id for msg in saved_messages]
    print(message_ids)
    return message_ids

async def send_messages(send_client, user_info, text, group_link):
    try:
        pbar = tqdm(total=len(user_info), desc="Sending messages", unit=" messages")

        for user in user_info:
            backoff_time = 1
            while True:
                try:
                    if user['id'] == (await send_client.get_me()).id:
                        pbar.update(1)
                        break

                    if user['username']:
                        entity = user['username']
                    else:
                        entity = await findEntity(user, send_client, group_link)
                        await asyncio.sleep(random.uniform(1.5, 3))
                    
                    print(f"Sending to: {entity}")
                    await send_client.send_message(entity, text)
                    await asyncio.sleep(random.uniform(1, 2))
                    pbar.update(1)
                    break
                except FloodWaitError as e:
                    print(f"Rate limit exceeded. Waiting for {e.seconds} seconds.")
                    await asyncio.sleep(e.seconds)
                    backoff_time = min(backoff_time * 2, 300)  # Max backoff of 5 minutes
                    print(f"\nRetrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                except UserPrivacyRestrictedError:
                    print(f"Failed to send message to {user['id']}: User's privacy settings prevent sending messages.")
                    break
                except UserNotMutualContactError:
                    print(f"Failed to send message to {user['id']}: User is not a mutual contact.")
                    break
                except Exception as e:
                    print(f"Failed to send message to {user['id']}: {e}")
                    backoff_time = min(backoff_time * 2, 300)  # Max backoff of 5 minutes
                    print(f"\nRetrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)

        pbar.close()
        print("Finished sending messages.")
    except Exception as e:
        print(f"An error occurred while sending messages: {e}")

async def forward_message(send_client, user_info, group_link):
    message_ids = await get_saved_message_ids(send_client)
    await send_media_with_caption(send_client, user_info, message_ids, group_link)
    await asyncio.sleep(1)

async def findEntity(user_info, send_client, group_link):
    try:
        entity = await send_client.get_entity(user_info['id'])
    except ValueError:
        participants = await send_client.get_participants(group_link)
        await asyncio.sleep(1)
        for participant in participants:
            if (participant.id == user_info['id'] or
                (participant.first_name == user_info['first_name'] and
                 participant.last_name == user_info['last_name'])):
                entity = participant
                break
        else:
            raise ValueError(f"User not found: {user_info['first_name']} {user_info['last_name']}")
    
    return entity

async def send_media_with_caption(send_client, user_info, message_ids, group_link):
    try:
        pbar = tqdm(total=len(user_info), desc="Sending media", unit=" users")

        for user in user_info:
            try:
                if user['id'] == (await send_client.get_me()).id:
                    pbar.update(1)
                    continue

                if user['username']:
                    entity = user['username']
                else:
                    entity = await findEntity(user, send_client, group_link)

                media_list = []
                captions = []

                for message_id in message_ids:
                    saved_message = await send_client.get_messages('me', ids=message_id)
                    if not saved_message or not saved_message.media:
                        continue

                    media_list.append(saved_message.media)
                    captions.append(saved_message.message if saved_message.message else "")

                await send_client.send_file(entity, media_list, caption="\n".join(captions))
                await asyncio.sleep(1)
                pbar.update(1)
            except Exception as e:
                print(f"Failed to send media to {user['id']}: {e}")

        pbar.close()
        print("Finished sending media.")
    except Exception as e:
        print(f"An error occurred while sending media: {e}")

async def mainFunc():
    crawl_client = TelegramClient(crawl_phone, crawl_api_id, crawl_api_hash)
    await crawl_client.start()
    print("Crawl client connected to Telegram")

    send_client = TelegramClient(send_phone, send_api_id, send_api_hash)
    await send_client.start()
    print("Send client connected to Telegram")
    group_link = "https://t.me/joinchat/D-vMUxZe1_5diITogcne7A"

    # group_link = "https://t.me/+TlkqeIbCWsgxMTI1"
    # await crawl_participants(crawl_client, group_link)
    # await asyncio.sleep(5)

    text = """大家好,各位ASM 既同事。我係你既一位前同事Alpha,依加係大陸開緊二手設備廠。\n
    貴公司一些設備係大陸有價有市,bond arm, motion card, vision card, sensor board, motors, camera board。\n
    全部高價回收。大家比各老板欺壓既同時, 不妨為自己謀下福利。你老細收四半,揸波子, 你就做到七半八半。每年四月review, 你又係得個吉。\n
    大陸好多同事都同我地依邊合作,開名車,賺好多錢。\n
    香港, 馬拉,菲律賓,泰國,新加坡。\n
    只要你安全有貨, 我地就會有人收。好既爛既都收。好過你日做夜做, 份糧又雞水咁多。\n
    usdt 加密貨幣交易全部安全可靠。歡迎聯絡我, 問下都的。 @slappoop   安全第一, ASM養老同時賺下外快"""

    user_info = await load_user_info()
    batch_size = 30
    delay_between_batches = 15

    start_id = 550533262  # Define the starting ID here
    start_index = next((index for index, user in enumerate(user_info) if user['id'] == start_id), 0)

    # Create a list of send clients
    # send_clients = [send_client, send_client_2]
    send_client_2 = crawl_client
    # You can add more clients to this list if needed
    # For example:
    # send_client_3 = TelegramClient('session_name_3', 'api_id_3', 'api_hash_3')
    # await send_client_3.start()
    # send_clients.append(send_client_3)

    async def send_batch(client, batch, text, group_link):
        await send_messages(client, batch, text, group_link)
        await asyncio.sleep(random.uniform(0.5, 2))
        # await forward_message(client, batch, group_link)

    for i in range(start_index, len(user_info), batch_size * 2):
        batch1 = user_info[i:i + batch_size]
        batch2 = user_info[i + batch_size:i + batch_size * 2]
        
        # Create tasks for parallel execution
        task1 = asyncio.create_task(send_batch(send_client, batch1, text, group_link))
        task2 = asyncio.create_task(send_batch(send_client_2, batch2, text, group_link))
        
        # Wait for both tasks to complete
        await task1
        await task2
        await asyncio.sleep(random.uniform(3, delay_between_batches))

if __name__ == "__main__":
    asyncio.run(mainFunc())
