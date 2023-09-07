from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Method:
    name: str
    start_point: Tuple[int, int]
    end_point: Tuple[int, int]
    comment: List[str] | None = None
    test: List[str] | None = None
    status: str = "new"
