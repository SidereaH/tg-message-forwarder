from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramForbiddenError,
)

log = logging.getLogger("forwarder")


@dataclass
class TelegramForwarder:
    bot: Bot

    async def send_text(self, *, to_chat_id: int, to_thread_id: int | None, text: str) -> None:
        # Можно увеличить таймаут на отправку (по умолчанию иногда маловат)
        await self.bot.send_message(
            chat_id=to_chat_id,
            text=text,
            message_thread_id=to_thread_id,
            request_timeout=30,   # <-- добавь
        )

    async def forward(
        self,
        *,
        to_chat_id: int,
        to_thread_id: int | None,
        from_chat_id: int,
        message_id: int,
        text: str | None = None,
    ) -> None:
        try:
            log.info("Forward try from=%s msg=%s -> to=%s thread=%s", from_chat_id, message_id, to_chat_id, to_thread_id)
            await self.bot.forward_message(
                chat_id=to_chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id,
                message_thread_id=to_thread_id,
                request_timeout=30,  # <-- добавь
            )
            log.info("Forward OK from=%s msg=%s -> to=%s", from_chat_id, message_id, to_chat_id)
            return

        except TelegramBadRequest as e:
            # forward не сработал — пробуем fallback для "not found"
            msg = str(e).lower()
            log.warning("Forward FAIL from=%s msg=%s -> to=%s: %s", from_chat_id, message_id, to_chat_id, e)

            if "message to forward not found" not in msg or not text:
                return

        except (TelegramNetworkError, TelegramForbiddenError) as e:
            # сети/бан/нет диалога — просто логируем и не падаем
            log.warning("Forward FAIL (network/forbidden) from=%s msg=%s -> to=%s: %s", from_chat_id, message_id, to_chat_id, e)
            return

        # fallback repost (и он тоже может падать — ЛОВИМ!)
        try:
            await self.send_text(to_chat_id=to_chat_id, to_thread_id=to_thread_id, text=text)
            log.info("Repost OK -> to=%s", to_chat_id)
        except TelegramForbiddenError as e:
            # Часто бывает: юзер не нажал /start, бот заблокирован, нет прав в чате
            log.warning("Repost FAIL (forbidden) -> to=%s: %s", to_chat_id, e)
        except TelegramNetworkError as e:
            log.warning("Repost FAIL (network timeout) -> to=%s: %s", to_chat_id, e)
        except TelegramBadRequest as e:
            log.warning("Repost FAIL (bad request) -> to=%s: %s", to_chat_id, e)
