from telethon import TelegramClient, sync
import os, dotenv, asyncio, pytz, re
from datetime import datetime, timezone

dotenv.load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')

class Fetcher():
    def __init__(self):
        self.client = TelegramClient('session_name', api_id, api_hash)

    async def start(self):
        await self.client.start(phone=phone_number)

    def remove_links(self, text):
        # remove everything in format []()
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)
        return text

    async def get_messages(self, channel_name, from_date=None, to_date=None):
        channel = await self.client.get_entity(channel_name)
        messages = await self.client.get_messages(channel, limit=100)
        messages = messages[::-1]

        messages_filtered = []
        for message in messages:
            if not message.text:
                continue
            if from_date:
                if message.date < from_date:
                    continue
            if to_date:
                if message.date > to_date:
                    continue

            hours = (datetime.now(tz=pytz.UTC) - message.date).seconds/3600
            
            # if message.reactions:
            #     reactions = message.reactions.results
            #     reactions = sorted(reactions, key=lambda x: x.count, reverse=True)
            #     if reactions[0].count < min(hours*1000, 1000):
            #         continue
            
            message.channel = channel_name
            message.link = f"https://t.me/{channel_name}/{message.id}"

            message.text = self.remove_links(message.text)

            messages_filtered.append(message)

        return messages_filtered
    
    async def channel_exists(self, channel_name):
        try:
            await self.client.get_entity(channel_name)
            return True
        except:
            return False
        
    async def disconnect(self):
        await self.client.disconnect()

async def main():
    fetcher = Fetcher()
    await fetcher.start()
    messages = await fetcher.get_messages('insiderUKR', from_date=datetime(2024, 9, 18, 6, tzinfo=timezone.utc))
    reactions = messages[0].reactions.results
    reactions = sorted(reactions, key=lambda x: x.count, reverse=True)
    print(reactions[0].count, reactions[0].reaction)

if __name__ == "__main__":
    asyncio.run(main())