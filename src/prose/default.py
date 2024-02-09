import os
import fire
import fire.core
from prose.dao.blob.blob_repository import BlobRepository

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


class Default:

    def __init__(self, config: Config):
        self._config = config
        self._config_repo = ConfigRepository()
        self._stage_repo = StageRepository()
        self._ref_repo = RefRepository()
        self._commit_repo = CommitRepository()
        self._blob_repo = BlobRepository()
        self._parser = ParserJava()
        self._llm = LLMOpenAI(self._parser)

    def status(self) -> None:
        """Show the working tree status.
        """
        stage = self._stage_repo.load()
        if stage is not None:
            TreeWalker(self._config).status(stage)

    def diff(self, object: str) -> None:
        """Provide the diff contents or details of repository objects.

        Args:
            object (str): The name of the object to diff.
        """
        stage = self._stage_repo.load()
        if stage is not None:
            TreeWalker(self._config).diff(stage, object)

    def cat(self, object: str) -> None:
        """Provide contents or details of repository objects.

        Args:
            object (str): The name of the object to show.
        """
        print(self._blob_repo.load(object))

    def add(self, src_path: str):
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
        tree_root = TreeWriter(self._config, self._parser, self._llm).write(src_path)
        if tree_root is not None:
            self._stage_repo.save(Stage(tree_root))
        ref = self._ref_repo.load(self._config.branch)
        if ref is not None:
            commit = self._commit_repo.load(ref)
        if commit is None or commit.tree != tree_root:
            panic("There are some undocumented or untested code.")

    def commit(self) -> None:
        """Parses a source tree.

        Prose collects undocumented classes and methods, proposes comments and tests using LLM. Prose aborts if some
        undocumented or untested classes or methods are found.
        """
        parent = self._ref_repo.load(self._config.branch)
        index = self._stage_repo.load()
        if index is not None:
            commit_content = Commit(index.tree, parent)
            commit_digest = self._commit_repo.save(commit_content)
            self._ref_repo.save(self._config.branch, commit_digest)
