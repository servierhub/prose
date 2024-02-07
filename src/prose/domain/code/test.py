from typing import Any
from dataclasses import asdict, dataclass, field


@dataclass
class Test:
    signature: str
    code: list[str] = field(default_factory=list)

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
