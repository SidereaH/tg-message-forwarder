from __future__ import annotations
from dataclasses import dataclass
from aiogram import Router
from aiogram.types import Message

from src.application.use_cases import ProcessIncomingMessage
from src.domain.models import MessageView

import logging
from aiogram.filters import Command

router = Router()
log = logging.getLogger("forwarder")


@router.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(
        f"chat_id={message.chat.id}\n"
        f"thread_id={getattr(message, 'message_thread_id', None)}\n"
        f"user_id={(message.from_user.id if message.from_user else None)}"
    )

@router.message(Command("ping"))
async def ping(message: Message):
    await message.answer("pong")

def log_msg(m: Message, prefix: str):
    log.info(
        "%s chat=%s type=%s thread=%s content=%s from_user=%s is_bot=%s sender_chat=%s",
        prefix,
        m.chat.id,
        m.chat.type,
        getattr(m, "message_thread_id", None),
        m.content_type,
        bool(m.from_user),
        (m.from_user.is_bot if m.from_user else None),
        bool(m.sender_chat),
    )
