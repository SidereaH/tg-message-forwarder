from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Any
import yaml

from src.domain.models import Route, Source, Destination, FilterPolicy

@dataclass
class InMemoryRouteRepository:
    routes: Sequence[Route]

    @classmethod
    def from_yaml(cls, path: str) -> "InMemoryRouteRepository":
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        routes: list[Route] = []
        for r in raw.get("routes", []):
            src = r["source"]
            destinations = [
                Destination(chat_id=d["chat_id"], thread_id=d.get("thread_id"))
                for d in r.get("destinations", [])
            ]
            filters = r.get("filters", {})
            fp = FilterPolicy(
                allow_bots=bool(filters.get("allow_bots", True)),
                allow_humans=bool(filters.get("allow_humans", True)),
                allow_channels=bool(filters.get("allow_channels", True)),
                allowed_content_types=filters.get("allowed_content_types"),
            )
            routes.append(
                Route(
                    id=str(r["id"]),
                    source=Source(chat_id=src["chat_id"], thread_id=src.get("thread_id")),
                    destinations=destinations,
                    filters=fp,
                    enabled=bool(r.get("enabled", True)),
                )
            )
        return cls(routes=routes)

    async def list_enabled_routes(self) -> Sequence[Route]:
        return [r for r in self.routes if r.enabled]
