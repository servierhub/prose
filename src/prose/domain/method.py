from dataclasses import dataclass

@dataclass
class Method:
    name: str
    start_point: (int)
    end_point: (int)
    comment: (str) | None = None
    test: (str) | None = None
    status: str = "new"
