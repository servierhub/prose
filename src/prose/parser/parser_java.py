from tree_sitter import Language, Parser, TreeCursor

from prose.parser.code import Code
from prose.parser.parser_base import ParserBase
from prose.domain.file import File
from prose.domain.clazz import Class
from prose.domain.method import Method

JAVA_LANGUAGE = Language("build/grammar.so", "java")
JAVA_DOC_FRAMEWORK = "JAVADOC"
JAVA_TEST_FRAMEWORK = "JUNIT"


class ParserJava(ParserBase):
    def __init__(self):
        self.parser = Parser()
        self.parser.set_language(JAVA_LANGUAGE)

    def parse(self, code: Code) -> None:
        tree = self.parser.parse(lambda _, p: code.get_bytes_at(p))
        cursor = tree.walk()
        self._parse_class(code, cursor, code.file)
        self._parse_method(code, cursor, code.file)
        self._parse_method(code, cursor, code.file)

    def _parse_class(self, code: Code, cursor: TreeCursor, file: File) -> None:
        # Go inside program
        cursor.goto_first_child()

        # Find the first class
        while cursor.node.type != "class_declaration":
            cursor.goto_next_sibling()
        class_start_point = cursor.node.start_point
        class_end_point = cursor.node.end_point
        cursor.goto_first_child()

        # Find the class identifier
        while cursor.node.type != "identifier":
            cursor.goto_next_sibling()
        class_name = code.get_str_between(
            cursor.node.start_point, cursor.node.end_point
        )

        if file.clazz is None or file.clazz.name != class_name:
            file.clazz = Class(class_name, class_start_point, class_end_point)
        else:
            file.clazz.start_point = class_start_point
            file.clazz.end_point = class_end_point

        # Find the class body
        while cursor.node.type != "class_body":
            cursor.goto_next_sibling()
        cursor.goto_first_child()

    def _parse_method(self, code: Code, cursor: TreeCursor, file: File) -> None:
        # Find the next method
        while cursor.node.type != "method_declaration":
            cursor.goto_next_sibling()
        method_start_point = cursor.node.start_point
        method_end_point = cursor.node.end_point

        # Find the method identifier
        child_cursor = cursor.copy()
        child_cursor.goto_first_child()
        while child_cursor.node.type != "identifier":
            child_cursor.goto_next_sibling()
        method_name = code.get_str_between(
            child_cursor.node.start_point, child_cursor.node.end_point
        )

        method = next(filter(lambda x: x.name == method_name, file.methods), None)
        if method is None:
            file.methods.append(Method(method_name, method_start_point, method_end_point))
        else:
            method.start_point = method_start_point
            method.end_point = method_end_point

        # Find the next method
        cursor.goto_next_sibling()
