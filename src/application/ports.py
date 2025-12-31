from __future__ import annotations
from typing import Protocol, Sequence
from src.domain.models import Route, MessageView, Destination

class RouteRepository(Protocol):
    async def list_enabled_routes(self) -> Sequence[Route]: ...

class Forwarder(Protocol):
    async def forward(
        self,
        *,
        to_chat_id: int,
        to_thread_id: int | None,
        from_chat_id: int,
        message_id: int,
    ) -> None: ...
    async def send_text(self, *, to_chat_id: int, to_thread_id: int | None, text: str) -> None: ...

