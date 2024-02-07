from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Tree:
    type: str
    digest: str
    name: str

    @staticmethod
    def of(data: dict) -> Tree:
        return Tree(**data)

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
