from typing import Callable

from prose.parser.code import Code
from prose.domain.clazz import Class
from prose.domain.method import Method
from prose.parser.parser_java import JAVA_DOC_FRAMEWORK, JAVA_TEST_FRAMEWORK


class LLMBase:
    def commentify_class(
        self,
        clazz: Class,
        methods: list[Method],
        filter: Callable[[str], str] | None = None,
    ) -> None:
        pass

    def commentify_method(
        self, code: Code, method: Method, filter: Callable[[str], str] | None = None
    ) -> None:
        pass

    def testify_method(
        self, code: Code, method: Method, filter: Callable[[str], str] | None = None
    ) -> None:
        pass
