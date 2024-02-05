from __future__ import annotations

from typing import Any, List, Tuple
from dataclasses import asdict, dataclass


@dataclass
class Method:
    name: str
    signature: str
    digest: str
    start_point: Tuple[int, int]
    end_point: Tuple[int, int]
    comment: List[str] | None
    tests: List[Tuple[str, Any]] | None = None

    def asdict(self) -> dict[str, Method]:
        return asdict(self)
