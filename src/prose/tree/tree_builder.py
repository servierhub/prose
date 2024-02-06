import os
import re

from tqdm import tqdm
from prose.domain.clazz import Class
from prose.domain.method import Method
from prose.domain.prose_object import ProseObject

from prose.llm.llm_openai import LLMOpenAI
from prose.domain.file import File
from prose.dao.file_repository import FileRepository
from prose.parser.code import Code
from prose.parser.parser_java import ParserJava
from prose.util.util import get_digest_file


class TreeBuilder:
    def __init__(self):
        self.file_repo = FileRepository()
        self.parser = ParserJava()
        self.llm = LLMOpenAI()

    def build(self, src_path: str) -> str | None:
        digest_objects = {}
        for args in os.walk(src_path, topdown=False):
            digest_objects = self._build_node(digest_objects, *args)
        return digest_objects.get("")

    def _build_node(
        self,
        digest_objects: dict[str, str],
        root: str,
        folders: list[str],
        files: list[str],
    ) -> dict[str, str]:
        if folders == [] and files == []:
            return digest_objects

        blob_content = [
            ProseObject("tree", digest_objects[folder], folder)
            for folder in folders
            if digest_objects.get(folder) is not None
        ] + [
            self._build_file(
                root, file, get_digest_file(os.path.join(root, file))
            )
            for file in files
        ]
        blob_digest = self.file_repo.save_blob(blob_content)

        parent_object = os.path.basename(root)
        digest_objects[parent_object] = blob_digest
        return digest_objects

    def _build_file(self, root: str, file: str, file_digest: str) -> ProseObject:
        if self.file_repo.exists_blob(file_digest):
            return ProseObject("file", file_digest, file)

        file_object = self._parse_one_file(os.path.join(root, file))

        blob_content = []
        if file_object.clazz is not None and file_object.clazz.digest is not None:
            blob_content += [
                self._build_clazz(file_object.clazz)
            ] + [
                self._build_method(method)
                for method in file_object.clazz.methods
                if method.digest is not None
            ]

        self.file_repo.save_blob(blob_content, file_digest)

        return ProseObject("file", file_digest, file)

    def _build_clazz(self, clazz: Class) -> ProseObject:
        assert clazz.digest is not None

        if self.file_repo.exists_blob(clazz.digest):
            return ProseObject("clazz", clazz.digest, self.parser.to_signature(clazz.signature))

        blob_content = []
        if clazz.has_llm_comment and clazz.comment is not None:
            blob_content += [
                self._build_comment(clazz.signature, clazz.comment)
            ]
        self.file_repo.save_blob(blob_content, clazz.digest)

        return ProseObject("clazz", clazz.digest, self.parser.to_signature(clazz.signature))

    def _build_method(self, method: Method) -> ProseObject:
        assert method.digest is not None

        if self.file_repo.exists_blob(method.digest):
            return ProseObject("method", method.digest, self.parser.to_signature(method.signature))

        blob_content = []
        if method.has_llm_comment and method.comment is not None:
            blob_content += [
                self._build_comment(method.signature, method.comment)
            ]
        if method.tests is not None:
            for test in method.tests:
                blob_content += [
                    self._build_test(*test)
                ]
        self.file_repo.save_blob(blob_content, method.digest)

        return ProseObject("method", method.digest, self.parser.to_signature(method.signature))

    def _build_comment(self, name, comment) -> ProseObject:
        blob_content = "\n".join(comment)
        blob_digest = self.file_repo.save_blob(blob_content)
        return ProseObject("comment", blob_digest, self.parser.to_signature(name))

    def _build_test(self, name, test) -> ProseObject:
        blob_content = "\n".join(test)
        blob_digest = self.file_repo.save_blob(blob_content)
        return ProseObject("test", blob_digest, self.parser.to_signature(name))

    def _parse_one_file(self, path: str) -> File:
        print(f"Parsing {path}")

        file = self.file_repo.find(path)
        if file is None:
            file = File.of(path)

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
        if method.digest is None or self.file_repo.exists_blob(method.digest):
            return

        if method.comment is None:
            self.llm.commentify_method(code, method)

        if method.tests is None:
            self.llm.testify_method(code, method)
