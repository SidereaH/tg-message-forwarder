from __future__ import annotations

import logging
from dataclasses import dataclass

from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.tl.types import User, Channel

from src.application.use_cases import ProcessIncomingMessage
from src.domain.models import MessageView

log = logging.getLogger("mtproto")

def detect_content_type(msg) -> str:
    # минимально нужное для твоего allowed_content_types
    if msg.message is not None:
        return "text"
    if msg.photo:
        return "photo"
    if msg.video:
        return "video"
    if msg.sticker:
        return "sticker"
    if msg.document:
        return "document"
    return "unknown"

def get_thread_id(msg) -> int | None:
    rt = getattr(msg, "reply_to", None)
    if rt is None:
        return None

    if getattr(rt, "forum_topic", False):
        return getattr(rt, "reply_to_top_id", None) or getattr(rt, "reply_to_msg_id", None)

    return None


@dataclass
class MtprotoListener:
    api_id: int
    api_hash: str
    session_str: str
    uc: ProcessIncomingMessage
    allowed_chat_ids: Sequence[int] = () 

    def __post_init__(self):
        self.client = TelegramClient(StringSession(self.session_str), self.api_id, self.api_hash)

    async def start(self) -> None:
        await self.client.connect()
        if not await self.client.is_user_authorized():
            raise RuntimeError("MTProto client is not authorized. Regenerate TG_USER_SESSION.")

        if self.allowed_chat_ids:
            self.client.add_event_handler(
                self._on_new_message,
                events.NewMessage(incoming=True, chats=list(self.allowed_chat_ids)),
            )
            log.info("MTProto listener started (filtered chats=%s)", list(self.allowed_chat_ids))
        else:
            self.client.add_event_handler(
                self._on_new_message,
                events.NewMessage(incoming=True),
            )
            log.info("MTProto listener started (no chat filter)")

        await self.client.run_until_disconnected()

    async def _on_new_message(self, event: events.NewMessage.Event) -> None:
        msg = event.message
        chat = await event.get_chat()
        chat_id = utils.get_peer_id(chat)  

        sender = await event.get_sender()
        from_is_channel = not isinstance(sender, User)
        from_is_bot = None
        from_is_human = None

        if isinstance(sender, User):
            from_is_bot = bool(getattr(sender, "bot", False))
            from_is_human = not from_is_bot
        elif isinstance(sender, Channel):
            from_is_channel = True

        thread_id = get_thread_id(msg)
        ctype = detect_content_type(msg)

        rt = getattr(msg, "reply_to", None)
        log.info(
            "MT IN chat=%s msg_id=%s thread=%s type=%s bot=%s forum=%s r_msg=%s r_top=%s",
            chat_id, msg.id, thread_id, ctype, from_is_bot,
            (getattr(rt, "forum_topic", None) if rt else None),
            (getattr(rt, "reply_to_msg_id", None) if rt else None),
            (getattr(rt, "reply_to_top_id", None) if rt else None),
        )

        text = msg.message if msg.message else None

        mv = MessageView(
            chat_id=chat_id,
            message_id=msg.id,
            thread_id=thread_id,
            from_is_bot=from_is_bot,
            from_is_human=from_is_human,
            from_is_channel=from_is_channel,
            content_type=ctype,
            text=text
        )

        try:
            await self.uc.execute(mv)
        except Exception:
            log.exception("UC execution failed for chat=%s msg_id=%s", chat_id, msg.id)
        return
