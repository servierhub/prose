import os
import re
import json
import operator

from tqdm import tqdm
from itertools import chain
from typing import Iterable, Tuple
from prose.domain.commit_object import CommitObject
from prose.domain.prose_object import ProseObject

from prose.llm.llm_openai import LLMOpenAI
from prose.domain.file import File
from prose.dao.file_repository import FileRepository
from prose.merger.merger_java import MergerJava
from prose.parser.code import Code
from prose.parser.parser_java import ParserJava
from prose.util.util import get_digest_object, get_digest_file, get_digest_string, panic


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
        digest_objects = {}
        commit = CommitObject("", changes=[])
        for args in os.walk(src_path, topdown=False):
            digest_objects, commit = self._build_tree(src_path, digest_objects, commit, *args)

        if len(commit.changes) > 0:
            commit_digest = get_digest_object(commit.asdict())
            self.file_repo.save_object(commit_digest, commit.asdict())
            self.file_repo.save_ref("main", commit_digest)
            panic("Found some undocumented or untested methods, abort!")


    def merge(self, inplace: bool) -> None:
        for file in self.file_repo.findall():
            self._merge_one_file(file, inplace)

    def _build_tree(self, src_path: str, digest_objects: dict, commit: CommitObject, root: str, folders: list[str], files: list[str]) -> Tuple[dict, CommitObject]:
        if folders == [] and files == []:
            return digest_objects, commit

        parent_object = os.path.basename(root)

        content = []
        for folder in folders:
            if digest_objects.get(folder) is not None:
                content.append(ProseObject("tree", digest_objects[folder], folder).asdict())

        for file in files:
            file_digest = get_digest_file(os.path.join(root, file))
            content.append(ProseObject("file", file_digest, file).asdict())

            if not self.file_repo.exists_object(file_digest):
                file_object = self._parse_one_file(os.path.join(root, file))
                file_content = []

                if file_object.clazz is not None:
                    file_content.append(ProseObject("clazz", file_object.clazz.digest, file_object.clazz.name).asdict())

                    if not self.file_repo.exists_object(file_object.clazz.digest):
                        clazz_content = []

                        if file_object.clazz.comment is not None:
                                comment_content = "\n".join(file_object.clazz.comment)
                                comment_digest = get_digest_string(comment_content)
                                self.file_repo.save_object(comment_digest, comment_content)
                                clazz_content.append(ProseObject("comment", comment_digest, file_object.clazz.name).asdict())

                        self.file_repo.save_object(file_object.clazz.digest, clazz_content)
                        commit.changes.append(file_object.clazz.digest)

                    for method in file_object.clazz.methods:
                        file_content.append(ProseObject("method", method.digest, method.name).asdict())

                        if not self.file_repo.exists_object(method.digest):
                            method_content = []

                            if method.comment is not None:
                                comment_content = "\n".join(method.comment)
                                comment_digest = get_digest_string(comment_content)
                                self.file_repo.save_object(comment_digest, comment_content)
                                method_content.append(ProseObject("comment", comment_digest, method.signature).asdict())

                            if method.tests is not None:
                                for test in method.tests:
                                    test_content = "\n".join(test[1])
                                    test_digest = get_digest_string(test_content)
                                    self.file_repo.save_object(test_digest, test_content)
                                    method_content.append(ProseObject("test", test_digest, test[0]).asdict())

                            self.file_repo.save_object(method.digest, method_content)
                            commit.changes.append(method.digest)

                self.file_repo.save_object(file_digest, file_content)

        content_digest = get_digest_object(content)

        if os.path.relpath(root, src_path) == '.':
            commit.tree = content_digest

        self.file_repo.save_object(content_digest, content)

        digest_objects[parent_object] = content_digest
        return digest_objects, commit

    def _parse_one_file(self, path: str) -> File:
        print(f"Parsing {path}")
        file = self.file_repo.find(path)
        if file is None:
            file = File.of(path)

        code = self._parse_code(file)

        if file.clazz is not None:
            for i in tqdm(range(0, len(file.clazz.methods) + 1), ncols=80):
                if i == len(file.clazz.methods):
                    if file.clazz.comment is None:
                        self.llm.commentify_class(file.clazz)
                else:
                    method = file.clazz.methods[i]
                    if not self.file_repo.exists_object(method.digest):
                        if method.comment is None:
                            self.llm.commentify_method(code, method)
                        if method.tests is None:
                            self.llm.testify_method(code, method)
        return file

    def _parse_code(self, file: File) -> Code:
        code = Code(file)
        code.load()
        self.parser.parse(code)
        return code

    def _merge_one_file(self, file: File, inplace: bool) -> None:
        print(f"Merging {file.path}")
        code = self._parse_code(file)
        self.merger.merge_test(code, file)
        self.merger.merge_code(code, file)
