import difflib
import os
import pydoc

from prose.dao.blob.blob_repository import BlobRepository
from prose.dao.blob.commit_repository import CommitRepository
from prose.dao.blob.config_repository import ConfigRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.dao.blob.stage_repository import StageRepository
from prose.domain.blob.commit import Commit
from prose.domain.blob.config import Config
from prose.domain.blob.stage import Stage
from prose.domain.blob.tree import Tree
from prose.llm.openai.llm_openai import LLMOpenAI
from prose.parser.java.parser_java import ParserJava
from prose.tree.tree_writer import TreeWriter
from prose.tree.tree_walker import TreeWalker
from prose.util.util import die, panic


class DefaultOp:

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
        if stage is None:
            return die("No files staged")

        output = [
            f"stage {stage.tree}",
            ""
        ]

        def diff(file: Tree, path: str) -> None:
            output.extend(self._diff(file, os.path.join(stage.path, path)))
        TreeWalker(self._config).walk(stage.tree, diff)

        pydoc.pager("\n".join(output))

    def diff(self, object: str) -> None:
        """Provide the diff contents or details of repository objects.

        Args:
            object (str): The name of the object to diff.
        """
        stage = self._stage_repo.load()
        if stage is None:
            return die("No files staged")

        output = [
            f"stage {stage.tree}",
            ""
        ]

        def diff_one_object(file: Tree, path: str) -> None:
            if object == file.digest:
                output.extend(self._diff(file, os.path.join(stage.path, path)))
        TreeWalker(self._config).walk(stage.tree, diff_one_object)

        pydoc.pager("\n".join(output))

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
        if tree_root is None:
            return die("No files to add.")

        changes = []
        def collect_change(file: Tree, path: str) -> None:
            changes.append(os.path.join(file.digest, path))
        TreeWalker(self._config).walk(tree_root, collect_change)
        if len(changes) > 0:
            stage = Stage(tree_root, src_path)
            self._stage_repo.save(stage)
        else:
            stage = self._stage_repo.load() or Stage(tree_root, src_path)

        ref = self._ref_repo.load(self._config.branch)
        if ref is not None:
            commit = self._commit_repo.load(ref)
        else:
            commit = None
        if commit is None or commit.tree != stage.tree:
            panic("There are some undocumented or untested code.")

    def merge(self) -> None:
        """Merge a source tree back to the original locations.
        """
        stage = self._stage_repo.load()
        if stage is None:
            return die("No files staged.")

        def rewrite_file(file: Tree, path: str) -> None:
            self._rewrite_file(file, os.path.join(stage.path, path))
        TreeWalker(self._config).walk(stage.tree, rewrite_file)

    def commit(self, merge: bool = False) -> None:
        """Record changes to the repository.

        Args:
            merge (bool): Merge files before commit.
        """
        stage = self._stage_repo.load()
        if stage is None:
            return die("No files staged.")

        parent = self._ref_repo.load(self._config.branch)
        if parent is not None:
            commit = self._commit_repo.load(parent)
            if commit is not None and commit.tree == stage.tree:
                return die("Nothing to commit, up-to-date.")

        if merge:
            self.merge()

        commit_content = Commit(stage.tree, stage.path, parent)
        commit_digest = self._commit_repo.save(commit_content)
        self._ref_repo.save(self._config.branch, commit_digest)

    def _diff(self, comment_or_test: Tree, path: str) -> list[str]:
        blob_content = self._blob_repo.load(comment_or_test.digest)
        if blob_content is not None:
            comment_or_test_content = blob_content.splitlines()
        else:
            comment_or_test_content = []

        original_path = os.path.join(self._config.base_path, path, comment_or_test.name)
        if comment_or_test.type == "test":
            original_path = original_path.replace("main", "test")
        if os.path.exists(original_path):
            with open(original_path, "r") as f:
                original_content = f.read().splitlines()
        else:
            original_content = []

        output = [
            f"{comment_or_test.type} {comment_or_test.digest}",
            f"Path: {original_path}",
            ""
        ]
        for line in difflib.unified_diff(
            original_content,
            comment_or_test_content,
            tofile=original_path,
            fromfile=comment_or_test.digest,
            lineterm="",
        ):
            output += [line]
        output += [""]
        return output

    def _rewrite_file(self, comment_or_test: Tree, path: str) -> None:
        blob_content = self._blob_repo.load(comment_or_test.digest)
        if blob_content is not None:
            comment_or_test_content = blob_content

            original_path = os.path.join(self._config.base_path, path, comment_or_test.name)
            if comment_or_test.type == "test":
                original_path = original_path.replace("main", "test")

            original_parent_path = os.path.dirname(original_path)
            os.makedirs(original_parent_path, exist_ok=True)

            with open(original_path, "w") as f:
                f.write(comment_or_test_content)
