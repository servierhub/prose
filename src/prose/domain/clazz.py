from dataclasses import dataclass


@dataclass
class Class:
    name: str
    start_point: (int)
    end_point: (int)
    comment: (str) | None = None
    status: str = "new"
