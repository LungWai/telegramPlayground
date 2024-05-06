from telethon.sync import TelegramClient

from telethon.tl.types import InputMessagesFilterPhotos, InputPeerUser
from tqdm import tqdm
import time

crawl_api_id = '27312057'
crawl_api_hash = '0e9aeb04cbce227238a0faaeabec3341'
crawl_phone = '+85260245331'

send_api_id = '23688237'
send_api_hash = 'b4c894b6ad4e7c8b813b22a56871aee9'
send_phone = '+85261404506'



def crawl_participants(crawl_client, group_link):
    participants = crawl_client.get_participants(group_link)
    user_info = []

    for p in participants:
        user_info.append({
            'id': p.id,
            'username': p.username,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'access_hash': p.access_hash
        })
        time.sleep(0.3)

    with open('user_info.json', 'w') as f:
        import json
        json.dump(user_info, f, indent=4)

    print("Participant information serialized to 'user_info.json'.")

def load_user_info():
    import json
    with open('user_info.json', 'r') as f:
        return json.load(f)

def get_saved_message_ids(client):
    saved_messages = client.get_messages('me', limit=None)
    message_ids = [msg.id for msg in saved_messages]
    print(message_ids)
    return message_ids

def send_messages(send_client, user_info, text):
    """Send a message to each user using their serialized entity information."""
    from telethon.tl.types import InputPeerUser

    try:
        pbar = tqdm(total=len(user_info), desc="Sending messages", unit=" messages")

        for user in user_info:
            try:
                # Reconstruct the InputPeerUser object
                entity = InputPeerUser(user_id=user['id'], access_hash=user['access_hash'])
                print(entity)
                send_client.send_message(entity, text)
                pbar.update(1)
                time.sleep(1)
            except Exception as e:
                print(f"Failed to send message to {user['id']}: {e}")

        pbar.close()
        print("Finished sending messages.")
    except Exception as e:
        print(f"An error occurred while sending messages: {e}")

def forward_message(send_client, user_info):
    """Forward saved messages to each user using their serialized entity information."""
    message_ids = get_saved_message_ids(send_client)
    send_media_with_caption(send_client, user_info, message_ids)

def send_media_with_caption(send_client, user_info, message_ids):
    """Send media with captions to each user using their serialized entity information."""
    from telethon.tl.types import InputPeerUser

    try:
        pbar = tqdm(total=len(user_info), desc="Sending media", unit=" users")

        for user in user_info:
            try:
                # Reconstruct the InputPeerUser object
                entity = InputPeerUser(user_id=user['id'], access_hash=user['access_hash'])

                media_list = []
                captions = []

                for message_id in message_ids:
                    saved_message = send_client.get_messages('me', ids=message_id)
                    if not saved_message or not saved_message.media:
                        continue

                    media_list.append(saved_message.media)
                    captions.append(saved_message.message if saved_message.message else "")

                send_client.send_file(entity, media_list, caption="\n".join(captions))
                pbar.update(1)
                time.sleep(1)
            except Exception as e:
                print(f"Failed to send media to {user['id']}: {e}")

        pbar.close()
        print("Finished sending media.")
    except Exception as e:
        print(f"An error occurred while sending media: {e}")

def mainFunc():
    # Initialize the crawl client
    crawl_client = TelegramClient(crawl_phone, crawl_api_id, crawl_api_hash)
    crawl_client.start()
    print("Crawl client connected to Telegram")

    # Initialize the send client
    # send_client = TelegramClient(send_phone, send_api_id, send_api_hash)
    # send_client.start()
    # print("Send client connected to Telegram")

    group_link = "https://t.me/+TlkqeIbCWsgxMTI1"

    # Use crawl client to gather participant information
    crawl_participants(crawl_client, group_link)

    # Load user information and use send client to send messages
    user_info = load_user_info()
    send_messages(crawl_client, user_info, text="Hi")
    forward_message(crawl_client, user_info)

if __name__ == "__main__":
    mainFunc()
