from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ProseObject:
    type: str
    digest: str
    name: str

    @staticmethod
    def of(data: dict) -> ProseObject:
        return ProseObject(**data)

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
