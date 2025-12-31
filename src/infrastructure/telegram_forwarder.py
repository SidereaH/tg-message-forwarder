from __future__ import annotations
from dataclasses import dataclass
from aiogram import Bot

@dataclass
class TelegramForwarder:
    bot: Bot

    async def forward(
        self,
        *,
        to_chat_id: int,
        to_thread_id: int | None,
        from_chat_id: int,
        message_id: int,
    ) -> None:
        await self.bot.forward_message(
            chat_id=to_chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            message_thread_id=to_thread_id,
        )
