from __future__ import annotations

from dataclasses import asdict, dataclass, field

from prose.domain.method import Method


@dataclass
class Class:
    name: str
    signature: str
    digest: str
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    comment: list[str] | None = None
    methods: list[Method] = field(default_factory=list)

    def asdict(self) -> dict[str, Class]:
        return asdict(self)

