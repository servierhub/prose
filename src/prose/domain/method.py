from __future__ import annotations

from typing import Any, List, Tuple
from dataclasses import asdict, dataclass


@dataclass
class Method:
    name: str
    signature: str
    digest: str | None = None
    start_point: Tuple[int, int] | None = None
    end_point: Tuple[int, int] | None = None
    has_llm_comment: bool = False
    comment: List[str] | None = None
    tests: List[Tuple[str, Any]] | None = None

    def asdict(self) -> dict[str, Method]:
        return asdict(self)
