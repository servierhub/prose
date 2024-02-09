import os

from prose.dao.code.file_repository import FileRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.dao.blob.tree_repository import TreeRepository
from prose.dao.blob.blob_repository import BlobRepository
from prose.domain.blob.config import Config
from prose.domain.code.file import File
from prose.domain.blob.tree import Tree
from prose.llm.llm_base import LLMBase
from prose.merger.merger import Merger
from prose.parser.parser_base import ParserBase
from prose.util.util import get_digest_file


class TreeWriter:
    def __init__(self, config: Config, parser: ParserBase, llm: LLMBase):
        self.config = config
        self.file_repo = FileRepository(parser, llm)
        self.ref_repo = RefRepository()
        self.tree_repo = TreeRepository()
        self.blob_repo = BlobRepository()

    def write(self, src_path: str) -> str | None:
        digest_objects = {}
        for args in os.walk(os.path.join(self.config.base_path, src_path), topdown=False):
            digest_objects = self._write_tree(digest_objects, *args)
        return digest_objects.get(os.path.basename(src_path)) or digest_objects.get("")

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
            if self.file_repo.get_parser().filter(file)
        ]
        digest_objects[os.path.basename(root)] = self.tree_repo.save(blob_content)
        return digest_objects

    def _write_file(self, root: str, file: str, file_digest: str) -> Tree:

        if self.tree_repo.exists(file_digest):
            return Tree("file", file_digest, file)

        code_file = self.file_repo.load(os.path.join(root, file))
        if code_file.clazz is None:
            blob_content = []
        else:
            blob_content = [
                self._write_comment(os.path.join(root, file), code_file),
                self._write_tests(os.path.join(root, file), code_file),
            ]

        if len(blob_content) > 0 and blob_content[0].type == "comment":
            file_digest = blob_content[0].digest

        self.tree_repo.save(blob_content, file_digest)
        return Tree("file", file_digest, file)

    def _write_comment(self, path: str, code_file: File) -> Tree:
        assert code_file.clazz is not None

        comment_merger = Merger(path)

        if (
            code_file.clazz.start_point is not None
            and code_file.clazz.comment is not None
        ):
            comment_merger.merge(code_file.clazz.start_point, code_file.clazz.comment)

        for method in code_file.clazz.methods:
            if (
                method.start_point is not None
                and method.comment is not None
                and method.has_llm_comment
            ):
                comment_merger.merge(method.start_point, method.comment)

        blob_digest = self.blob_repo.save(comment_merger.get_text())
        return Tree("comment", blob_digest, os.path.basename(path))

    def _write_tests(self, path: str, code_file: File) -> Tree:
        assert code_file.clazz is not None

        test_path = path.replace("main", "test").replace(
            code_file.name, "Test" + code_file.name
        )
        if not os.path.exists(test_path):
            src_lines = self.file_repo.get_parser().get_test_stub(code_file)
            test_merger = Merger(src_lines)
        else:
            test_merger = Merger(test_path)


        for method in code_file.clazz.methods:
            if method.tests is not None and method.has_llm_tests:
                for test in method.tests:
                    if test_merger.find(test.signature) is None:
                        end_of_code = test_merger.find_last(
                            self.file_repo.get_parser().get_end_of_code()
                        )
                        if end_of_code is not None:
                            test_merger.merge((end_of_code[0], 4), [""] + test.code)

        blob_digest = self.blob_repo.save(test_merger.get_text())
        return Tree("test", blob_digest, os.path.basename(test_path))
