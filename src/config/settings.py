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

    def allowed_updates_list(self) -> Optional[Sequence[str]]:
        if not self.allowed_updates:
            return None
        return [x.strip() for x in self.allowed_updates.split(",") if x.strip()]
