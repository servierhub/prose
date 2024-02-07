from typing import Callable

from prose.parser.code import Code
from prose.domain.code.clazz import Class
from prose.domain.code.method import Method


class LLMBase:
    def commentify_class(self, clazz: Class) -> None:
        pass

    def commentify_method(self, method: Method) -> None:
        pass

    def testify_method(self, method: Method) -> None:
        pass
