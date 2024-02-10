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
from prose.util.util import get_digest_file, removeNonesIfAny


class TreeWriter:
    def __init__(self, config: Config, parser: ParserBase, llm: LLMBase):
        self.config = config
        self.file_repo = FileRepository(parser, llm)
        self.ref_repo = RefRepository()
        self.tree_repo = TreeRepository()
        self.blob_repo = BlobRepository()

    def write(self, src_path: str) -> str | None:
        digest_objects = {}
        full_path = os.path.join(self.config.base_path, src_path)
        for args in os.walk(full_path, topdown=False):
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

        blob_content = removeNonesIfAny(
            [
                Tree("tree", digest_objects[folder], folder)
                for folder in folders
                if digest_objects.get(folder) is not None
            ]
            + [
                self._write_file(os.path.join(root, file))
                for file in files
                if self.file_repo.get_parser().filter(file)
            ]
        )
        digest_objects[os.path.basename(root)] = self.tree_repo.save(blob_content)
        return digest_objects

    def _write_file(self, file_path: str) -> Tree | None:
        file_digest = get_digest_file(file_path)
        if self.tree_repo.exists(file_digest):
            return None

        code_file = self.file_repo.load(file_path)
        if code_file.clazz is None:
            return None

        with open(file_path, "r") as f:
            self.blob_repo.save(f.read(), file_digest)

        blob_content = removeNonesIfAny(
            [
                self._write_comment(file_path, code_file, file_digest),
                self._write_tests(file_path, code_file),
            ]
        )
        blob_digest = self.tree_repo.save(blob_content)

        return Tree("file", blob_digest, os.path.basename(file_path))

    def _write_comment(self, file_path: str, file: File, file_digest: str) -> Tree:
        assert file.clazz is not None

        comment_merger = Merger(file_path)

        if (
            file.clazz.start_point is not None
            and file.clazz.comment is not None
            and file.clazz.has_llm_comment
        ):
            comment_merger.merge(file.clazz.start_point, file.clazz.comment)

        for method in file.clazz.methods:
            if (
                method.start_point is not None
                and method.comment is not None
                and method.has_llm_comment
            ):
                comment_merger.merge(method.start_point, method.comment)

        if comment_merger.is_modified():
            file_digest = self.blob_repo.save(comment_merger.get_text())

        return Tree("comment", file_digest, os.path.basename(file_path))

    def _write_tests(self, file_path: str, file: File) -> Tree | None:
        assert file.clazz is not None

        if file.clazz.disable_tests:
            return None

        test_path = file_path.replace("/main/", "/test/", 1).replace(
            file.name, "Test" + file.name
        )
        if not os.path.exists(test_path):
            src_lines = self.file_repo.get_parser().get_test_stub(file)
            test_merger = Merger(src_lines)
        else:
            test_merger = Merger(test_path)

        for method in file.clazz.methods:
            if method.tests is not None and method.has_llm_tests:
                first_test = True
                for test in method.tests:
                    if test_merger.find(test.signature) is None:
                        end_of_code = test_merger.find_last(
                            self.file_repo.get_parser().get_end_of_code()
                        )
                        if end_of_code is not None:
                            if first_test:
                                test_merger.merge((end_of_code[0], 4), test.code)
                                first_test = False
                            else:
                                test_merger.merge((end_of_code[0], 4), [""] + test.code)

        blob_digest = self.blob_repo.save(test_merger.get_text())
        return Tree("test", blob_digest, os.path.basename(test_path))
