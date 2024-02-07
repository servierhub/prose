import fire
import fire.core

from prose.dao.blob.commit_repository import CommitRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.domain.blob.commit import Commit
from prose.llm.openai.llm_openai import LLMOpenAI
from prose.parser.java.parser_java import ParserJava
from prose.tree.tree_writer import TreeWriter
from prose.tree.tree_walker import TreeWalker
from prose.util.util import panic


class Main:
    """A CLI tool to bring the power of LLM to the CI/CD by ensuring documentation and unit tests for an
    entire source tree.

    Prose is a CLI tool to document and generate tests for Java and Python projects using LLM. It allows for easy addition of
    new languages and LLM systems, such as Azure OpenAI (as the default). Prose parses source code and generates comments
    and tests incrementally. Prose can also be integrated into a CI/CD pipeline and abort if there are classes or methods
    without documentation or tests. Additionally, Prose adds a summary to the README file.
    """

    def __init__(self):
        self.ref_repo = RefRepository()
        self.commit_repo = CommitRepository()
        self.parser = ParserJava()
        self.llm = LLMOpenAI(self.parser)

    def __enter__(self):
        print("Loading config ...")
        return self

    def __exit__(self, *_):
        pass

    def log(self) -> None:
        """Log the collected comments and tests.
        """
        TreeWalker().walk()

    def cat(self, digest: str) -> None:
        """Output the content of a blob.

        Args:
            digest (str): the digest of the blob.
        """
        TreeWalker().cat(digest)

    def parse(self, src_path: str) -> None:
        """Parses a source tree.

        Prose collects undocumented classes and methods, proposes comments and tests using LLM. Prose aborts if some
        undocumented or untested classes or methods are found.

        Args:
            src_path (str): the source tree to parse.
        """
        tree_root =  TreeWriter(self.parser, self.llm).write(src_path)
        if tree_root is not None:
            commit_content = Commit(tree_root)
            commit_digest = self.commit_repo.save(commit_content)
            self.ref_repo.save("main", commit_digest)
            panic("Found some undocumented or untested methods, abort!")

    def merge(self, inplace: bool = False) -> None:
        """Merges all comments and tests marked "review".

        Args:
            inplace (bool): Modify the source code in place, otherwise create a copy.
        """
        pass

if __name__ == "__main__":
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(Main)
