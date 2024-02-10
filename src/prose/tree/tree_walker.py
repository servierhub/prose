import os
from typing import Callable, TypeAlias

from prose.dao.blob.blob_repository import BlobRepository
from prose.dao.blob.commit_repository import CommitRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.dao.blob.stage_repository import StageRepository
from prose.dao.blob.tree_repository import TreeRepository
from prose.domain.blob.config import Config
from prose.domain.blob.stage import Stage
from prose.domain.blob.tree import Tree

TreeWalkerFunc: TypeAlias = Callable[[Tree, str], None]


class TreeWalker:
    def __init__(self, config: Config):
        self.config = config
        self.stage_repo = StageRepository()
        self.commit_repo = CommitRepository()
        self.tree_repo = TreeRepository()
        self.blob_repo = BlobRepository()

    def walk(self, root_digest: str, func: TreeWalkerFunc) -> None:
        root = self.tree_repo.load(root_digest) or []
        self._walk_rec(root, "", func)

    def _walk_rec(self, tree: list[Tree], path: str, func: TreeWalkerFunc) -> None:
        for node in tree:
            if node.type == "tree":
                self._walk_rec(
                    self.tree_repo.load(node.digest) or [],
                    os.path.join(path, node.name),
                    func,
                )
            elif node.type == "file":
                comment_or_tests = self.tree_repo.load(node.digest) or []
                for comment_or_test in comment_or_tests:
                    func(comment_or_test, path)
