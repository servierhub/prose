from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Commit:
    tree: str
    path: str
    parent: str | None = None

    @staticmethod
    def of(data: dict) -> Commit:
        return Commit(**data)

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

