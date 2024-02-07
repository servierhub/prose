import os

from prose.dao.code.file_repository import FileRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.dao.blob.tree_repository import TreeRepository
from prose.dao.blob.blob_repository import BlobRepository
from prose.domain.code.clazz import Class
from prose.domain.code.method import Method
from prose.domain.blob.tree import Tree
from prose.llm.llm_base import LLMBase
from prose.parser.parser_base import ParserBase
from prose.util.util import get_digest_file


class TreeWriter:
    def __init__(self, parser: ParserBase, llm: LLMBase):
        self.file_repo = FileRepository(parser, llm)
        self.ref_repo = RefRepository()
        self.tree_repo = TreeRepository()
        self.blob_repo = BlobRepository()

    def write(self, src_path: str) -> str | None:
        digest_objects = {}
        for args in os.walk(src_path, topdown=False):
            digest_objects = self._write_tree(digest_objects, *args)
        return digest_objects.get("")

    def _write_tree(
        self,
        digest_objects: dict[str, str],
        root: str,
        folders: list[str],
        files: list[str],
    ) -> dict[str, str]:

        if folders == [] and files == []:
            return digest_objects

        blob_content = [
            Tree("tree", digest_objects[folder], folder)
            for folder in folders
            if digest_objects.get(folder) is not None
        ] + [
            self._write_file(root, file, get_digest_file(os.path.join(root, file)))
            for file in files
        ]
        digest_objects[os.path.basename(root)] = self.tree_repo.save(blob_content)
        return digest_objects

    def _write_file(self, root: str, file: str, file_digest: str) -> Tree:

        if self.tree_repo.exists(file_digest):
            return Tree("file", file_digest, file)

        code_file = self.file_repo.load(os.path.join(root, file))

        blob_content = []
        if code_file.clazz is not None and code_file.clazz.digest is not None:
            blob_content += [self._write_clazz(code_file.clazz)] + [
                self._write_method(method)
                for method in code_file.clazz.methods
                if method.digest is not None
            ]
        self.tree_repo.save(blob_content, file_digest)
        return Tree("file", file_digest, file)

    def _write_clazz(self, clazz: Class) -> Tree:
        assert clazz.digest is not None

        if self.tree_repo.exists(clazz.digest):
            return Tree("clazz", clazz.digest, clazz.signature)

        blob_content = []
        if clazz.has_llm_comment and clazz.comment is not None:
            blob_content += [self._write_comment(clazz.signature, clazz.comment)]
        self.tree_repo.save(blob_content, clazz.digest)

        return Tree("clazz", clazz.digest, clazz.signature)

    def _write_method(self, method: Method) -> Tree:
        assert method.digest is not None

        if self.tree_repo.exists(method.digest):
            return Tree("method", method.digest, method.signature)

        blob_content = []
        if method.has_llm_comment and method.comment is not None:
            blob_content += [self._write_comment(method.signature, method.comment)]
        if method.tests is not None:
            for test in method.tests:
                blob_content += [self._write_test(test.signature, test.code)]
        self.tree_repo.save(blob_content, method.digest)

        return Tree("method", method.digest, method.signature)

    def _write_comment(self, name: str, comment: list[str]) -> Tree:
        blob_content = "\n".join(comment)
        blob_digest = self.blob_repo.save(blob_content)
        return Tree("comment", blob_digest, name)

    def _write_test(self, name: str, test: list[str]) -> Tree:
        blob_content = "\n".join(test)
        blob_digest = self.blob_repo.save(blob_content)
        return Tree("test", blob_digest, name)

