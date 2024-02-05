from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class CommitObject:
    tree: str

    def asdict(self) -> dict[str, CommitObject]:
        return asdict(self)

