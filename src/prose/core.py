import os
import re
import sys
import operator

from tqdm import tqdm
from itertools import chain
from functools import reduce
from typing import Iterable

from prose.llm.llm_openai import LLMOpenAI
from prose.domain.file import File
from prose.dao.file_repository import FileRepository
from prose.merger.merger_java import MergerJava
from prose.parser.code import Code
from prose.parser.parser_java import ParserJava
from prose.util.util import panic


class Prose:
    def __init__(self):
        self.file_repo = FileRepository()
        self.parser = ParserJava()
        self.llm = LLMOpenAI()
        self.merger = MergerJava()

    def __enter__(self):
        self.file_repo.load("prose.json")
        return self

    def __exit__(self, *_):
        self.file_repo.save("prose.json")

    def parse(self, src_path: str) -> None:
        all_file_pathes = self._collect_file_pathes(src_path)
        all_results = map(self._parse_one_file, all_file_pathes)
        has_some_new = reduce(operator.or_, all_results, False)
        if has_some_new:
            panic("Found some undocumented or untested methods, abort!")

    def merge(self, inplace: bool) -> None:
        for file in self.file_repo.findall():
            self._merge_one_file(file, inplace)

    def _parse_one_file(self, path: str) -> bool:
        print(f"Parsing {path}")
        file = self.file_repo.find(path)
        if file is None:
            file = File.of(path)

        code = self._parse_code(file)

        has_new = False
        for i in tqdm(range(0, len(file.methods) + 1), ncols=80):
            if i == len(file.methods):
                if file.clazz is not None:
                    if file.clazz.comment is None:
                        self.llm.commentify_class(file.clazz, file.methods)
                    if file.clazz.status == "new":
                        has_new = True
            else:
                method = file.methods[i]
                if method.comment is None:
                    self.llm.commentify_method(code, method)
                if method.test is None:
                    self.llm.testify_method(
                        code, method, filter=lambda s: re.sub(r"```.*\n?", "", s)
                    )
                if method.status == "new":
                    has_new = True

        self.file_repo.upsert(file)

        return has_new

    def _merge_one_file(self, file: File, inplace: bool) -> None:
        print(f"Merging {file.path}")
        code = self._parse_code(file)
        self.merger.merge_test(code, file)
        self.merger.merge_code(code, file)

    def _collect_file_pathes(self, src_path: str) -> Iterable[str]:
        return chain.from_iterable(
            [
                [os.path.join(root, file) for file in self.parser.filter(files)]
                for root, _, files in os.walk(src_path)
            ]
        )

    def _parse_code(self, file: File) -> Code:
        code = Code(file)
        code.load()
        self.parser.parse(code)
        return code
