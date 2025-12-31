from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, Sequence

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(..., alias="BOT_TOKEN")

    routes_path: str = Field("src/config/routes.yaml", alias="ROUTES_PATH")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    drop_pending_updates: bool = Field(True, alias="DROP_PENDING_UPDATES")

    # Можно ограничить, какие апдейты получать (опционально)
    # Пример: "message,edited_message"
    allowed_updates: Optional[str] = Field(None, alias="ALLOWED_UPDATES")

    tg_api_id: int = Field(..., alias="TG_API_ID")
    tg_api_hash: str = Field(..., alias="TG_API_HASH")
    tg_user_session: str = Field(..., alias="TG_USER_SESSION")

    def allowed_updates_list(self) -> Optional[Sequence[str]]:
        if not self.allowed_updates:
            return None
        return [x.strip() for x in self.allowed_updates.split(",") if x.strip()]
    
    mt_allowed_chat_ids: str = Field("-1003393646784", alias="MT_ALLOWED_CHAT_IDS")

    def mt_allowed_chat_ids_list(self) -> list[int]:
        raw = self.mt_allowed_chat_ids.strip()
        if not raw:
            return []
        out: list[int] = []
        for part in raw.split(","):
            p = part.strip()
            if not p:
                continue
            out.append(int(p))
        return out
