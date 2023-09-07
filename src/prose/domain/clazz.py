from dataclasses import dataclass


@dataclass
class Class:
    name: str
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    comment: list[str] | None = None
    status: str = "new"
