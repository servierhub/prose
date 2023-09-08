import os
import re
import sys
import logging

from prose.llm.llm_openai import LLMOpenAI
from prose.domain.file import File
from prose.dao.file_repository import FileRepository
from prose.merger.merger_java import MergerJava
from prose.parser.code import Code
from prose.parser.parser_java import ParserJava

logging.basicConfig(level=logging.INFO)


class Prose:
    def __init__(self):
        self.file_repo = FileRepository()
        self.parser = ParserJava()
        self.llm = LLMOpenAI()
        self.merger = MergerJava()

    def parse(self) -> None:
        self.file_repo.load("prose.json")

        found_something_new = False
        for root, _, files in os.walk("data/src/main"):
            for file in files:
                if file.endswith(".java"):
                    found_something_new |= self._prosify_one_file(
                        os.path.join(root, file)
                    )

        self.file_repo.save("prose.json")

        if found_something_new:
            logging.error("Found new comments and tests, abort!")
            sys.exit(1)

    def merge(self, inplace: bool) -> None:
        self.file_repo.load("prose.json")

        for file in self.file_repo.findall():
            self._merge_one_file(file, inplace)

        self.file_repo.save("prose.json")

    def _prosify_one_file(self, path: str) -> bool:
        found_something_new = False

        file = self.file_repo.find(path)
        if file is None:
            file = File.of(path)
        logging.info(f"Parsing {file.path} ...")

        code = Code(file)
        if not code.load():
            logging.error(f"I/O Error: could not load the file '{file.path}'")
            sys.exit(1)
        self.parser.parse(code)

        for method in file.methods:
            if method.comment is None:
                logging.info(f"Processing method {method.name} ...")
                self.llm.commentify_method(code, method)
            if method.test is None:
                self.llm.testify_method(
                    code, method, filter=lambda s: re.sub(r"```.*\n?", "", s)
                )
            if method.status == "new":
                found_something_new = True

        if file.clazz is not None:
            if file.clazz.comment is None:
                logging.info(f"Processing class {file.clazz.name} ...")
                self.llm.commentify_class(file.clazz, file.methods)
            if file.clazz.status == "new":
                found_something_new = True

        self.file_repo.upsert(file)

        return found_something_new

    def _merge_one_file(self, file: File, inplace: bool) -> None:
        logging.info(f"Merging {file.path} ...")

        code = Code(file)
        if not code.load():
            logging.error(f"I/O Error: could not load the file '{file.path}'")
            sys.exit(1)
        self.parser.parse(code)

        self.merger.merge_test(code, file)
        self.merger.merge_code(code, file)
