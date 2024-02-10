import re

from collections.abc import Iterable
from typing import Tuple

from tree_sitter import Language, Parser, TreeCursor

from prose.parser.code import Code
from prose.parser.parser_base import ParserBase
from prose.domain.code.file import File
from prose.domain.code.clazz import Class
from prose.domain.code.method import Method
from prose.util.util import get_digest_string

JAVA_LANGUAGE = Language("/usr/local/share/prose/build/grammar.so", "java")
JAVA_DOC_FRAMEWORK = "JAVADOC"
JAVA_TEST_FRAMEWORK = "JUNIT"

JAVA_PROMPT_DOCUMENT_CLASS = f"""
Comment the class below by summarizing the {JAVA_DOC_FRAMEWORK} comments below.
Be sure to:
* Do not include too much details.
* Do not include any parameters or return.
* Do not include the class definition.
The final output must be a {JAVA_DOC_FRAMEWORK} comment.
"""

JAVA_PROMPT_DOCUMENT_METHOD = f"""
Comment the method below using {JAVA_DOC_FRAMEWORK} and by summarizing what the method do, not as steps but as a text.
Be sure to:
* Include always the list of parameters and return value at the end of the comment.
* Do not put the comments in the method body but only in the {JAVA_DOC_FRAMEWORK} section.
* Do not include the function body in the response.
The final output must be a valid {JAVA_DOC_FRAMEWORK} comment.
"""

JAVA_PROMPT_UNIT_TEST = f"""
Generate unit tests for the function below using {JAVA_TEST_FRAMEWORK} framework.
Be sure to:
* Extract all generated methods and remove everything else.
* Do not include the import and class definition.
"""

JAVA_IDENTIFIER = ["identifier", "scoped_identifier"]
JAVA_BLOCK_COMMENT = ["block_comment"]
JAVA_PACKAGE_DECLARATION = ["package_declaration"]
JAVA_CLASS_DECLARATION = ["class_declaration", "interface_declaration"]
JAVA_CLASS_BODY = ["class_body", "interface_body"]
JAVA_METHOD_DECLARATION = ["constructor_declaration", "method_declaration"]
JAVA_METHOD_BODY = ["constructor_body", "block", ";"]

JAVA_COMMENT_JAVADOC = r"^\s*\/\*\*\n(\s*\*.*\n)+\s*\*\/"
JAVA_TEST_FUNC = r"((?:@.+\n)+)([^@][^(]+\([^)]*\)[\s|\w]*)\s*({\n[^@]*\n\s*})\n"
JAVA_REMOVE_SPACE = r"\s+"


class ParserJava(ParserBase):
    def __init__(self):
        self.parser = Parser()
        self.parser.set_language(JAVA_LANGUAGE)

    def get_prompt_class_comment(self, clazz: Class) -> str | None:
        return "\n".join(
            [JAVA_PROMPT_DOCUMENT_CLASS, "Class: " + clazz.signature, ""]
            + ["\n".join(method.comment or []) + "\n" for method in clazz.methods]
        )

    def is_valid_class_comment(self, comment: str) -> bool:
        return re.search(JAVA_COMMENT_JAVADOC, comment) is not None

    def cleanup_class_comment(self, comment: str) -> list[str] | None:
        m = re.search(JAVA_COMMENT_JAVADOC, comment)
        if m is not None:
            return m.group(0).splitlines()

    def get_prompt_method_comment(self, method: Method) -> str | None:
        return "\n".join([JAVA_PROMPT_DOCUMENT_METHOD] + method.code)

    def is_valid_method_comment(self, comment: str) -> bool:
        return re.search(JAVA_COMMENT_JAVADOC, comment) is not None

    def cleanup_method_comment(self, comment: str) -> list[str] | None:
        m = re.search(JAVA_COMMENT_JAVADOC, comment)
        if m is not None:
            return m.group(0).splitlines()

    def get_prompt_method_tests(self, method: Method) -> str:
        return "\n".join([JAVA_PROMPT_UNIT_TEST] + method.code)

    def is_valid_method_tests(self, tests: str) -> bool:
        return re.search(JAVA_TEST_FUNC, tests) is not None

    def cleanup_method_tests(
        self, tests: str
    ) -> list[Tuple[list[str], list[str], list[str]]] | None:
        return [
            (
                decorator.strip().splitlines(),
                declaration.strip().splitlines(),
                body.strip().splitlines(),
            )
            for decorator, declaration, body in re.findall(JAVA_TEST_FUNC, tests)
        ]

    def get_test_stub(self, code_file: File) -> list[str]:
        assert code_file.clazz is not None
        return [
                "package " + code_file.clazz.package + ";\n"
                "\n",
                "import org.junit.Test;\n"
                "\n",
                "public class Test" + code_file.clazz.name + "\n",
                "{\n",
                "}\n"
            ]

    def get_end_of_code(self) -> str:
        return "}"

    def filter(self, file: str) -> bool:
        return file.endswith(".java")

    def parse(self, code: Code) -> None:
        tree = self.parser.parse(lambda _, p: code.get_bytes_at(p))  # type: ignore
        cursor = tree.walk()
        cursor.goto_first_child()
        self._parse_class_or_interface(code, cursor, code.file)
        if code.file.clazz is not None:
            while self._parse_method(code, cursor, code.file):
                pass

    def _parse_class_or_interface(self, code: Code, cursor: TreeCursor, file: File) -> None:
        package_name_point = self._parse_class_package_name(cursor)
        clazz_point, comment_point = self._accept_with_comment(cursor, JAVA_CLASS_DECLARATION)
        child_cursor = cursor.copy()
        child_cursor.goto_first_child()
        signature_point, name_point = self._parse_class_signature(child_cursor)

        # Collect class info

        clazz_package = code.get_str_between(*package_name_point) or ""
        clazz_name = code.get_str_between(*name_point) or ""
        clazz_signature = code.get_block_between(*signature_point) or ""
        clazz_code = code.get_block_between(*clazz_point) or ""
        clazz_digest = get_digest_string(clazz_code)
        clazz_comment = None
        if comment_point is not None:
            comment = code.get_block_between(*comment_point)
            if self.is_valid_class_comment(comment):
                clazz_comment = comment.splitlines()

        # Add class to file

        if file.clazz is None or file.clazz.signature != clazz_signature:
            file.clazz = Class(clazz_package, clazz_name, clazz_signature)
        file.clazz.digest = clazz_digest
        file.clazz.start_point = clazz_point[0]
        file.clazz.end_point = clazz_point[1]
        file.clazz.disable_tests = "interface" in clazz_signature
        file.clazz.has_llm_comment = False
        file.clazz.comment = clazz_comment

        # Find the class body
        cursor.goto_first_child()
        while cursor.node.type not in JAVA_CLASS_BODY:
            cursor.goto_next_sibling()
        cursor.goto_first_child()

    def _parse_class_package_name(
        self, cursor: TreeCursor
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        self._accept(cursor, JAVA_PACKAGE_DECLARATION)
        child_cursor = cursor.copy()
        child_cursor.goto_first_child()
        return self._accept(child_cursor, JAVA_IDENTIFIER)

    def _parse_class_signature(self, cursor: TreeCursor) -> Tuple[
        Tuple[Tuple[int, int], Tuple[int, int]],
        Tuple[Tuple[int, int], Tuple[int, int]],
    ]:
        signature_start_point = cursor.node.start_point
        name_point = self._accept(cursor, JAVA_IDENTIFIER)
        self._accept(cursor, JAVA_CLASS_BODY)
        assert cursor.node.prev_sibling is not None
        signature_point = (signature_start_point, cursor.node.prev_sibling.end_point)
        return (signature_point, name_point)

    def _parse_method(self, code: Code, cursor: TreeCursor, file: File) -> bool:
        assert file.clazz is not None

        try:
            method_point, comment_point = self._accept_with_comment(cursor, JAVA_METHOD_DECLARATION)
            child_cursor = cursor.copy()
            child_cursor.goto_first_child()
            signature_point, name_point = self._parse_method_signature(child_cursor)
        except:
            return False

        # Collect method info

        method_name = code.get_str_between(*name_point) or ""
        method_signature = code.get_block_between(*signature_point) or ""
        method_code = code.get_block_between(*method_point) or ""
        method_digest = get_digest_string(method_code)
        method_comment = None
        if comment_point is not None:
            comment = code.get_block_between(*comment_point)
            if self.is_valid_method_comment(comment):
                method_comment = comment.splitlines()

        # Add method to file

        method = next(
            filter(lambda x: x.signature == method_signature, file.clazz.methods), None
        )
        if method is None:
            method = Method(method_name, method_signature)
            file.clazz.methods.append(method)
        method.digest = method_digest
        method.start_point = method_point[0]
        method.end_point = method_point[1]
        method.code = method_code.splitlines()
        method.has_llm_comment = False
        method.comment = method_comment

        # Go to the next method
        cursor.goto_next_sibling()

        return True

    def _parse_method_signature(self, cursor: TreeCursor) -> Tuple[
        Tuple[Tuple[int, int], Tuple[int, int]],
        Tuple[Tuple[int, int], Tuple[int, int]],
    ]:
        signature_start_point = cursor.node.start_point
        name_point = self._accept(cursor, JAVA_IDENTIFIER)
        self._accept(cursor, JAVA_METHOD_BODY)
        assert cursor.node.prev_sibling is not None
        signature_point =  (signature_start_point, cursor.node.prev_sibling.end_point)
        return (signature_point, name_point)

    def _accept(self, cursor: TreeCursor, tokens: list[str]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        has_sibling = True
        while has_sibling and cursor.node.type not in tokens:
            has_sibling = cursor.goto_next_sibling()
        if not has_sibling:
            raise Exception(f"Tokens not found: {tokens}")
        return (cursor.node.start_point, cursor.node.end_point)

    def _accept_with_comment(self, cursor: TreeCursor, tokens: list[str]) -> Tuple[
        Tuple[Tuple[int, int], Tuple[int, int]],
        Tuple[Tuple[int, int], Tuple[int, int]] | None,
    ]:
        comment_point = None
        has_sibling = True
        while has_sibling and cursor.node.type not in tokens:
            if cursor.node.type in JAVA_BLOCK_COMMENT:
                comment_point = (cursor.node.start_point, cursor.node.end_point)
            else:
                comment_point = None
            has_sibling = cursor.goto_next_sibling()
        if not has_sibling:
            raise Exception(f"Tokens not found: {tokens}")
        return ((cursor.node.start_point, cursor.node.end_point), comment_point)
