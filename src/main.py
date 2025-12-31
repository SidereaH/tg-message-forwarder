import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from src.config.settings import Settings
from src.infrastructure.aiogram_app import router
from src.infrastructure.repo_inmemory import InMemoryRouteRepository
from src.infrastructure.telegram_forwarder import TelegramForwarder
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
    dp = Dispatcher()

    repo = InMemoryRouteRepository.from_yaml(settings.routes_path)
    forwarder = TelegramForwarder(bot=bot)
    uc = ProcessIncomingMessage(repo=repo, forwarder=forwarder)

    dp.update.middleware(UCMiddleware(uc))
    dp.include_router(router)

    await dp.start_polling(
        bot,
        allowed_updates=settings.allowed_updates_list(),
        drop_pending_updates=settings.drop_pending_updates,
    )

if __name__ == "__main__":
    asyncio.run(main())
