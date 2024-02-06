from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class ProseObject:
    type: str
    digest: str
    name: str

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
