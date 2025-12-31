from dataclasses import dataclass
from typing import Optional, Sequence

@dataclass(frozen=True)
class Source:
    chat_id: int
    thread_id: Optional[int] = None

@dataclass(frozen=True)
class Destination:
    chat_id: int
    thread_id: Optional[int] = None

@dataclass(frozen=True)
class FilterPolicy:
    allow_bots: bool = True
    allow_humans: bool = True
    allow_channels: bool = True
    allowed_content_types: Optional[Sequence[str]] = None  # None = любые

@dataclass(frozen=True)
class Route:
    id: str
    source: Source
    destinations: Sequence[Destination]
    filters: FilterPolicy
    enabled: bool = True


@dataclass(frozen=True)
class MessageView:
    chat_id: int
    message_id: int
    thread_id: Optional[int]
    from_is_bot: Optional[bool]
    from_is_human: Optional[bool]
    from_is_channel: bool
    content_type: str
    text: Optional[str] = None   # <-- добавь
