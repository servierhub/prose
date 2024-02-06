from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class CommitObject:
    tree: str
    parent: str | None = None

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

