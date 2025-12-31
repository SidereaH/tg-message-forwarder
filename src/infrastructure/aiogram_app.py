from __future__ import annotations
from dataclasses import dataclass
from aiogram import Router
from aiogram.types import Message

from src.application.use_cases import ProcessIncomingMessage
from src.domain.models import MessageView

router = Router()

@router.message()
async def on_any_message(message: Message, uc: ProcessIncomingMessage):
    from_user = message.from_user
    sender_chat = message.sender_chat  # если сообщение от имени чата/канала

    mv = MessageView(
        chat_id=message.chat.id,
        message_id=message.message_id,
        thread_id=getattr(message, "message_thread_id", None),
        from_is_bot=(from_user.is_bot if from_user else None),
        from_is_human=(False if (from_user and from_user.is_bot) else (True if from_user else None)),
        from_is_channel=sender_chat is not None,
        content_type=message.content_type,
    )

    await uc.execute(mv)
