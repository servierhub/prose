
from prose.domain.commit_object import CommitObject
from prose.llm.llm_openai import LLMOpenAI
from prose.domain.file import File
from prose.dao.file_repository import FileRepository
from prose.merger.merger_java import MergerJava
from prose.parser.code import Code
from prose.parser.parser_java import ParserJava
from prose.tree.tree_builder import TreeBuilder
from prose.util.util import get_digest_object, panic

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
        tree_root =  TreeBuilder().build(src_path)
        if tree_root is not None:
            commit_content = CommitObject(tree_root).asdict()
            commit_digest = get_digest_object(commit_content)
            self.file_repo.save_blob(commit_digest, commit_content)
            self.file_repo.save_ref("main", commit_digest)
            panic("Found some undocumented or untested methods, abort!")

    def merge(self, inplace: bool) -> None:
        for file in self.file_repo.findall():
            self._merge_one_file(file, inplace)

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
