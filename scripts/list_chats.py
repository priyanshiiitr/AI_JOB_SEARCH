import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / '.env')

from app.config import TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_PHONE, SESSION_DIR


async def main():
    client = TelegramClient(str(SESSION_DIR / 'job_agent'), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.start(phone=TELEGRAM_PHONE or None)

    print('\nChats visible to this Telegram account:\n')
    async for dialog in client.iter_dialogs():
        print(f'ID: {dialog.id:<15} | {dialog.name}')

    await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
