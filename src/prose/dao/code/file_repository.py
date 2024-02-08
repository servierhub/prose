import json
import os

from tqdm import tqdm

from prose.dao.blob.tree_repository import TreeRepository
from prose.domain.code.clazz import Class
from prose.domain.code.file import File
from prose.domain.code.method import Method
from prose.llm.llm_base import LLMBase
from prose.parser.code import Code
from prose.parser.parser_base import ParserBase


class FileRepository:

    def __init__(self, parser: ParserBase, llm: LLMBase):
        self.tree_repo = TreeRepository()
        self.parser = parser
        self.llm = llm
        pass

    def get_parser(self) -> ParserBase:
        return self.parser

    def get_lln(self) -> LLMBase:
        return self.llm

    def load(self, path: str) -> File:
        print(f"Loading {path} ...")

        file = File(os.path.basename(path), path)
        code = self._parse_code(file)
        if file.clazz is None:
            return file

        for i in tqdm(range(0, len(file.clazz.methods) + 1), ncols=80):
            if i == 0:
                self._parse_clazz(file.clazz)
            else:
                self._parse_method(file.clazz.methods[i - 1], code)

        return file

    def _parse_code(self, file: File) -> Code:
        code = Code(file)
        code.load()
        self.parser.parse(code)
        return code

    def _parse_clazz(self, clazz: Class) -> None:
        if clazz.comment is None:
            self.llm.commentify_class(clazz)

    def _parse_method(self, method: Method, code: Code) -> None:
        if method.digest is None or self.tree_repo.exists(method.digest):
            return

        if method.comment is None:
            self.llm.commentify_method(method)

        if method.tests is None:
            self.llm.testify_method(method)

