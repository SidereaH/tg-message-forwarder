import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

async def main():
    api_id = int(input("TG_API_ID: ").strip())
    api_hash = input("TG_API_HASH: ").strip()
    phone = input("PHONE (e.g. +7999...): ").strip()

    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start(phone=phone)

    print("\n=== TG_USER_SESSION ===")
    print(client.session.save())
    print("=======================\n")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
