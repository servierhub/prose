import os
import fire
import fire.core

from prose.dao.blob.commit_repository import CommitRepository
from prose.dao.blob.config_repository import ConfigRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.dao.blob.stage_repository import StageRepository
from prose.domain.blob.commit import Commit
from prose.domain.blob.config import Config
from prose.domain.blob.stage import Stage
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
        self.config_repo = ConfigRepository()
        self.stage_repo = StageRepository()
        self.ref_repo = RefRepository()
        self.commit_repo = CommitRepository()
        self.parser = ParserJava()
        self.llm = LLMOpenAI(self.parser)
        self.config = self.config_repo.load() or Config(".", "main")
        if not os.path.exists(self.config.src_path):
            panic("Source path not found")

    def branch(self, name: str) -> None:
        """List, create, or delete branches.

        Args:
            digest (str): the digest of the blob.
        """
        ref = self.ref_repo.load(name)
        if ref is not None:
            self.stage_repo.save(Stage(ref))
        self.config.branch = name
        self.config_repo.save(self.config)

    def status(self) -> None:
        """Show the working tree status.
        """
        TreeWalker().walk()

    def cat(self, object: str) -> None:
        """Provide contents or details of repository objects.

        Args:
            object (str): The name of the object to show.
        """
        TreeWalker().cat(object)

    def add(self, src_path: str | None = None):
        """Add file contents to the index.

        This command updates the index using the current content found in the working tree, to prepare the content
        staged for the next commit. It typically adds the current content of existing paths as a whole, but with some
        options it can also be used to add content with only part of the changes made to the working tree files applied,
        or remove paths that do not exist in the working tree anymore.

        The "index" holds a snapshot of the content of the working tree, and it is this snapshot that is taken as the
        contents of the next commit. Thus after making any changes to the working tree, and before running the commit
        command, you must use the add command to add any new or modified files to the index.

        This command can be performed multiple times before a commit. It only adds the content of the specified file(s)
        at the time the add command is run; if you want subsequent changes included in the next commit, then you must run
        git add again to add the new content to the index.

        The git status command can be used to obtain a summary of which files have changes that are staged for the next
        commit.

        Args:
            src_path (str): Files to add content from.
        """
        tree_root = TreeWriter(self.parser, self.llm).write(src_path or self.config.src_path)
        if tree_root is not None:
            self.stage_repo.save(Stage(tree_root))

    def commit(self) -> None:
        """Parses a source tree.

        Prose collects undocumented classes and methods, proposes comments and tests using LLM. Prose aborts if some
        undocumented or untested classes or methods are found.
        """
        parent = self.ref_repo.load(self.config.branch)
        index = self.stage_repo.load()
        if index is not None:
            commit_content = Commit(index.tree, parent)
            commit_digest = self.commit_repo.save(commit_content)
            self.ref_repo.save(self.config.branch, commit_digest)

    def merge(self, inplace: bool = False) -> None:
        """Merges all comments and tests marked "review".

        Args:
            inplace (bool): Modify the source code in place, otherwise create a copy.
        """
        pass

if __name__ == "__main__":
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(Main)
