import os
import pydoc
import difflib
from typing import Callable

from prose.dao.blob.blob_repository import BlobRepository
from prose.dao.blob.commit_repository import CommitRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.dao.blob.stage_repository import StageRepository
from prose.dao.blob.tree_repository import TreeRepository
from prose.domain.blob.config import Config
from prose.domain.blob.stage import Stage
from prose.domain.blob.tree import Tree


class TreeWalker:
    def __init__(self, config: Config):
        self.config = config
        self.stage_repo = StageRepository()
        self.commit_repo = CommitRepository()
        self.tree_repo = TreeRepository()
        self.blob_repo = BlobRepository()

    def diff(self, stage: Stage, object: str) -> None:
        output = [
            f"stage {stage.tree}",
            ""
        ]
        def show_diff_one_object(file: Tree, path: str) -> None:
            if object == file.digest:
                output.extend(self._get_diff(file, path))
        self.walk(stage.tree, show_diff_one_object)
        pydoc.pager("\n".join(output))

    def status(self, stage: Stage) -> None:
        output = [
            f"stage {stage.tree}",
            ""
        ]
        def show_diff(file: Tree, path: str) -> None:
            output.extend(self._get_diff(file, path))
        self.walk(stage.tree, show_diff)
        pydoc.pager("\n".join(output))

    def write(self, stage: Stage) -> None:
        self.walk(stage.tree, self._overwrite_content)

    def walk(self, root_tree: str, func: Callable[[Tree, str], None]) -> None:
        root = self.tree_repo.load(root_tree)
        if root is not None:
            self._walk_rec(root, "", func)

    def _walk_rec(
        self, tree: list[Tree] | None, path: str, func: Callable[[Tree, str], None]
    ) -> None:
        if tree is not None:
            for node in tree:
                if node.type == "tree":
                    self._walk_rec(
                        self.tree_repo.load(node.digest),
                        os.path.join(path, node.name),
                        func
                    )
                elif node.type == "file":
                    self._walk_file(
                        self.tree_repo.load(node.digest),
                        path,
                        func
                    )

    def _walk_file(
        self, objects: list[Tree] | None, path: str, func: Callable[[Tree, str], None]
    ) -> None:
        if objects is not None:
            for object in objects:
                func(object, path)

    def _get_diff(self, comment_or_test: Tree, path: str) -> list[str]:
        blob_content = self.blob_repo.load(comment_or_test.digest)
        if blob_content is not None:
            comment_or_test_content = blob_content.splitlines()
        else:
            comment_or_test_content = []

        original_path = os.path.join(self.config.base_path, path, comment_or_test.name)
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

    def _overwrite_content(self, comment_or_test: Tree, path: str) -> None:
        blob_content = self.blob_repo.load(comment_or_test.digest)
        if blob_content is not None:
            comment_or_test_content = blob_content.splitlines()
            original_path = os.path.join(self.config.base_path, path, comment_or_test.name)
            if comment_or_test.type == "test":
                original_path = original_path.replace("main", "test")
            with open(original_path, "r") as f:
                f.writelines(comment_or_test_content)
