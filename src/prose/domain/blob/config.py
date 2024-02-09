from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Config:
    base_path: str
    branch: str

    @staticmethod
    def of(data: dict) -> Config:
        return Config(**data)

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
