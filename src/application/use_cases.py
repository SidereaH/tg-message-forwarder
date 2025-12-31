from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from src.application.ports import RouteRepository, Forwarder
from src.domain.models import MessageView, Route

@dataclass
class ProcessIncomingMessage:
    repo: RouteRepository
    forwarder: Forwarder

    async def execute(self, msg: MessageView) -> int:
        routes: Sequence[Route] = await self.repo.list_enabled_routes()
        matched = 0

        for r in routes:
            if not r.enabled:
                continue

            # source match
            if r.source.chat_id != msg.chat_id:
                continue
            if r.source.thread_id is not None and r.source.thread_id != msg.thread_id:
                continue

            # filters
            fp = r.filters

            if msg.from_is_channel and not fp.allow_channels:
                continue

            # from_user может отсутствовать, тогда from_is_bot/from_is_human = None
            if msg.from_is_bot is True and not fp.allow_bots:
                continue
            if msg.from_is_human is True and not fp.allow_humans:
                continue

            if fp.allowed_content_types is not None and msg.content_type not in fp.allowed_content_types:
                continue

            # forward to all destinations
            for d in r.destinations:
                await self.forwarder.forward(
                    to_chat_id=d.chat_id,
                    to_thread_id=d.thread_id,
                    from_chat_id=msg.chat_id,
                    message_id=msg.message_id,
                )
            matched += 1

        return matched
