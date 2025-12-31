import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from src.config.settings import Settings
from src.infrastructure.aiogram_app import router
from src.infrastructure.repo_inmemory import InMemoryRouteRepository
from src.infrastructure.telegram_forwarder import TelegramForwarder
from src.infrastructure.mtproto_listener import MtprotoListener
from src.application.use_cases import ProcessIncomingMessage

class UCMiddleware(BaseMiddleware):
    def __init__(self, uc: ProcessIncomingMessage):
        super().__init__()
        self._uc = uc

    async def __call__(self, handler, event, data):
        data["uc"] = self._uc
        return await handler(event, data)

async def main():
    settings = Settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    bot = Bot(token=settings.bot_token)

    me = await bot.get_me()
    chat = await bot.get_chat(-1003393646784)
    print(me.id, chat.id)


    dp = Dispatcher()
    dp.include_router(router)

    repo = InMemoryRouteRepository.from_yaml(settings.routes_path)
    forwarder = TelegramForwarder(bot=bot)
    uc = ProcessIncomingMessage(repo=repo, forwarder=forwarder)

    dp.update.middleware(UCMiddleware(uc))

    listener = MtprotoListener(
        api_id=settings.tg_api_id,
        api_hash=settings.tg_api_hash,
        session_str=settings.tg_user_session,
        uc=uc,
        allowed_chat_ids=settings.mt_allowed_chat_ids_list(), 
    )

    # ВАЖНО: dp.start_polling блокирует — поэтому запускаем как task
    polling_task = asyncio.create_task(
        dp.start_polling(bot, drop_pending_updates=settings.drop_pending_updates)
    )
    listener_task = asyncio.create_task(listener.start())

    await asyncio.gather(polling_task, listener_task)

if __name__ == "__main__":
    asyncio.run(main())
