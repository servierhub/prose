from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Stage:
    tree: str

    @staticmethod
    def of(data: dict) -> Stage:
        return Stage(**data)

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

