from collections.abc import Iterable

from prose.parser.code import Code


class ParserBase:

    def filter(self, files: list[str]) -> Iterable[str]:
        return []

    def parse(self, code: Code) -> None:
        pass
