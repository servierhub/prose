from dataclasses import dataclass, asdict
from typing import Any

from prose.domain.code.clazz import Class


@dataclass
class File:
    name: str
    path: str
    clazz: Class | None = None

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
