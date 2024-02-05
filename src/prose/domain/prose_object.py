from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class ProseObject:
    type: str
    digest: str
    name: str

    def asdict(self) -> dict[str, ProseObject]:
        return asdict(self)
