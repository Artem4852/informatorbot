from telethon import TelegramClient, sync
import os, dotenv
from datetime import datetime, timezone

dotenv.load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

class Fetcher():
    def __init__(self):
        self.client = TelegramClient('session_name', api_id, api_hash)

        self.start()

    def start(self):
        self.client.start(phone=phone_number)

    def get_messages(self, channel_name, from_date=None, to_date=None):
        channel = self.client.get_entity(channel_name)

        messages = self.client.get_messages(channel, limit=100)

        messages = messages[::-1]

        messages_filtered = []
        for message in messages:
            if not message.text:
                continue
            if from_date:
                if message.date < from_date:
                    # print("Skipped", message.date)
                    continue
            if to_date:
                if message.date > to_date:
                    # print("Skipped", message.date)
                    continue
            # print("Added", message.date)
            messages_filtered.append(message)

        return messages_filtered

if __name__ == "__main__":
    fetcher = Fetcher()
    print(fetcher.get_messages('insiderUKR', from_date=datetime(2024, 9, 18, 6, tzinfo=timezone.utc)))