from __future__ import annotations

import os

from dataclasses import dataclass, field, asdict

from prose.domain.clazz import Class
from prose.domain.method import Method


@dataclass
class File:
    name: str
    path: str
    clazz: Class | None = None
    methods: list[Method] = field(default_factory=list)

    @staticmethod
    def of(data: dict | str) -> File:
        if isinstance(data, str):
            file_name = os.path.basename(data)
            return File(file_name, data)
        else:
            file = File(**data)
            file.clazz = Class(**data["clazz"])
            file.methods = [Method(**x) for x in data["methods"]]
            return file

    def asdict(self) -> dict[str, File]:
        return asdict(self)
