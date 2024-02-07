from typing import Any, Tuple
from dataclasses import asdict, dataclass, field

from prose.domain.code.test import Test


@dataclass
class Method:
    name: str
    signature: str
    digest: str | None = None
    start_point: Tuple[int, int] | None = None
    end_point: Tuple[int, int] | None = None
    code: list[str] = field(default_factory=list)
    has_llm_comment: bool = False
    comment: list[str] | None = None
    has_llm_tests: bool = False
    tests: list[Test] | None = None

    def asdict(self) -> dict[str, Any]:
        return asdict(self)
