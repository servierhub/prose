import re

from collections.abc import Iterable

from tree_sitter import Language, Parser, TreeCursor

from prose.parser.code import Code
from prose.parser.parser_base import ParserBase
from prose.domain.file import File
from prose.domain.clazz import Class
from prose.domain.method import Method
from prose.util.util import get_digest_string

JAVA_LANGUAGE = Language("build/grammar.so", "java")
JAVA_DOC_FRAMEWORK = "JAVADOC"
JAVA_TEST_FRAMEWORK = "JUNIT"

JAVA_IDENTIFIER = ["identifier"]
JAVA_BLOCK_COMMENT = ["block_comment"]
JAVA_CLASS_DECLARATION = ["class_declaration"]
JAVA_CLASS_BODY = ["class_body"]
JAVA_METHOD_DECLARATION = ["constructor_declaration", "method_declaration"]
JAVA_METHOD_BODY = ["constructor_body", "block"]

JAVA_IS_JAVADOC = r"^\s*\/\*\*\n(\s*\*.*\n)+\s*\*\/"
JAVA_REMOVE_SPACE = r"\s+"

class ParserJava(ParserBase):
    def __init__(self):
        self.parser = Parser()
        self.parser.set_language(JAVA_LANGUAGE)

    def to_signature(self, code: str) -> str:
        return re.sub(JAVA_REMOVE_SPACE, "", code)

    def filter(self, files: list[str]) -> Iterable[str]:
        return filter(lambda x: x.endswith(".java"), files)

    def parse(self, code: Code) -> None:
        tree = self.parser.parse(lambda _, p: code.get_bytes_at(p))  # type: ignore
        cursor = tree.walk()
        cursor.goto_first_child()
        self._parse_class(code, cursor, code.file)
        while self._parse_method(code, cursor, code.file):
            pass

    def _parse_class(self, code: Code, cursor: TreeCursor, file: File) -> None:
        clazz_start_point, clazz_end_point, comment_start_point, comment_end_point = (
            self._parse_class_declaration(cursor)
        )

        child_cursor = cursor.copy()
        child_cursor.goto_first_child()

        signature_start_point, signature_end_point, name_start_point, name_end_point = (
            self._parse_class_signature(child_cursor)
        )

        # Collect class info
        clazz_name = code.get_str_between(name_start_point, name_end_point) or ""
        clazz_signature = (
            code.get_block_between(signature_start_point, signature_end_point) or ""
        )
        clazz_code = code.get_block_between(clazz_start_point, clazz_end_point) or ""
        clazz_digest = get_digest_string(clazz_code)

        clazz_comment = None
        if comment_start_point is not None and comment_end_point is not None:
            comment = code.get_block_between(comment_start_point, comment_end_point)
            if re.search(JAVA_IS_JAVADOC, comment) is not None:
                clazz_comment = comment.splitlines()

        # Add class to file
        if file.clazz is None or file.clazz.signature != clazz_signature:
            file.clazz = Class(clazz_name, clazz_signature)
        file.clazz.digest = clazz_digest
        file.clazz.start_point = clazz_start_point
        file.clazz.end_point = clazz_end_point
        file.clazz.has_llm_comment = False
        file.clazz.comment = clazz_comment

        # Find the class body
        cursor.goto_first_child()
        while cursor.node.type not in JAVA_CLASS_BODY:
            cursor.goto_next_sibling()
        cursor.goto_first_child()

    def _parse_class_declaration(self, cursor: TreeCursor):
        comment_start_point = None
        comment_end_point = None
        while cursor.node.type not in JAVA_CLASS_DECLARATION:
            if cursor.node.type in JAVA_BLOCK_COMMENT:
                comment_start_point = cursor.node.start_point
                comment_end_point = cursor.node.end_point
            else:
                comment_start_point = None
                comment_end_point = None
            cursor.goto_next_sibling()
        clazz_start_point = cursor.node.start_point
        clazz_end_point = cursor.node.end_point
        return (
            clazz_start_point,
            clazz_end_point,
            comment_start_point,
            comment_end_point,
        )

    def _parse_class_signature(self, cursor: TreeCursor):
        signature_start_point = cursor.node.start_point
        name_start_point, name_end_point = self._parse_identifier(cursor)
        while cursor.node.type not in JAVA_CLASS_BODY:
            cursor.goto_next_sibling()
        assert cursor.node.prev_sibling is not None
        signature_end_point = cursor.node.prev_sibling.end_point
        return (
            signature_start_point,
            signature_end_point,
            name_start_point,
            name_end_point,
        )

    def _parse_method(self, code: Code, cursor: TreeCursor, file: File) -> bool:
        if file.clazz is None:
            return False

        try:
            (
                method_start_point,
                method_end_point,
                comment_start_point,
                comment_end_point,
            ) = self._parse_method_declaration(cursor)
        except:
            return False

        child_cursor = cursor.copy()
        child_cursor.goto_first_child()

        signature_start_point, signature_end_point, name_start_point, name_end_point = (
            self._parse_method_signature(child_cursor)
        )

        # Collect method info
        method_name = code.get_str_between(name_start_point, name_end_point) or ""
        method_signature = (
            code.get_block_between(signature_start_point, signature_end_point) or ""
        )
        method_code = code.get_block_between(method_start_point, method_end_point) or ""
        method_digest = get_digest_string(method_code)

        method_comment = None
        if comment_start_point is not None and comment_end_point is not None:
            comment = code.get_block_between(comment_start_point, comment_end_point)
            if re.search(JAVA_IS_JAVADOC, comment) is not None:
                method_comment = comment.splitlines()

        # Add method to file
        method = next(
            filter(lambda x: x.signature == method_signature, file.clazz.methods), None
        )
        if method is None:
            method = Method(method_name, method_signature)
            file.clazz.methods.append(method)
        method.digest = method_digest
        method.start_point = method_start_point
        method.end_point = method_end_point
        method.has_llm_comment = False
        method.comment = method_comment

        # Go to the next method
        cursor.goto_next_sibling()

        return True

    def _parse_method_declaration(self, cursor: TreeCursor):
        comment_start_point = None
        comment_end_point = None
        has_sibling = True
        while has_sibling and cursor.node.type not in JAVA_METHOD_DECLARATION:
            if cursor.node.type in JAVA_BLOCK_COMMENT:
                comment_start_point = cursor.node.start_point
                comment_end_point = cursor.node.end_point
            else:
                comment_start_point = None
                comment_end_point = None
            has_sibling = cursor.goto_next_sibling()
        if not has_sibling:
            raise Exception("No method found")
        method_start_point = cursor.node.start_point
        method_end_point = cursor.node.end_point
        return (
            method_start_point,
            method_end_point,
            comment_start_point,
            comment_end_point,
        )

    def _parse_method_signature(self, cursor: TreeCursor):
        signature_start_point = cursor.node.start_point
        name_start_point, name_end_point = self._parse_identifier(cursor)
        while cursor.node.type not in JAVA_METHOD_BODY:
            cursor.goto_next_sibling()
        assert cursor.node.prev_sibling is not None
        signature_end_point = cursor.node.prev_sibling.end_point
        return (
            signature_start_point,
            signature_end_point,
            name_start_point,
            name_end_point,
        )

    def _parse_identifier(self, cursor: TreeCursor):
        while cursor.node.type not in JAVA_IDENTIFIER:
            cursor.goto_next_sibling()
        name_start_point = cursor.node.start_point
        name_end_point = cursor.node.end_point
        return name_start_point, name_end_point
