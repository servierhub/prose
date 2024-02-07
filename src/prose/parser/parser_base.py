from collections.abc import Iterable
from typing import Tuple

from prose.domain.code.clazz import Class
from prose.domain.code.method import Method
from prose.parser.code import Code


class ParserBase:

    def get_prompt_class_comment(self, clazz: Class) -> str | None:
        return None

    def is_valid_class_comment(self, comment: str) -> bool:
        return False

    def cleanup_class_comment(self, comment: str) -> list[str] | None:
        return None

    def get_prompt_method_comment(self, method: Method) -> str | None:
        return None

    def is_valid_method_comment(self, comment: str) -> bool:
        return False

    def cleanup_method_comment(self, comment: str) -> list[str] | None:
        return None

    def get_prompt_method_tests(self, method: Method) -> str | None:
        return None

    def is_valid_method_tests(self, tests: str) -> bool:
        return False

    def cleanup_method_tests(self, tests: str) -> list[Tuple[list[str], list[str], list[str]]] | None:
        return None

    def filter(self, files: list[str]) -> Iterable[str]:
        return []

    def parse(self, code: Code) -> None:
        pass
