from prose.dao.blob.commit_repository import CommitRepository
from prose.dao.blob.config_repository import ConfigRepository
from prose.dao.blob.ref_repository import RefRepository
from prose.dao.blob.stage_repository import StageRepository
from prose.domain.blob.config import Config
from prose.domain.blob.stage import Stage
from prose.util.util import panic


class BranchOp:

    def __init__(self, config: Config):
        self._config = config
        self._config_repo = ConfigRepository()
        self._stage_repo = StageRepository()
        self._ref_repo = RefRepository()
        self._commit_repo = CommitRepository()

    def show(self):
        """Show the current branch.
        """
        print(self._config.branch)

    def checkout(self, name: str):
        """Switch to a branch.

        If the branch doesn't exist, a new branch is created from the current branch.

        Args:
            name (str): the name of the branch.
        """
        ref = self._ref_repo.load(name)
        if ref is not None:
            commit = self._commit_repo.load(ref)
            if commit is not None:
                self._stage_repo.save(Stage(commit.tree, commit.path))
        else:
            ref = self._ref_repo.load(self._config.branch)
            if ref is not None:
                self._ref_repo.save(name, ref)
        self._config.branch = name
        self._config_repo.save(self._config)

    def delete(self, name: str):
        """Delete a branch.

        The branch to delete can not be the current branch.

        Args:
            name (str): the name of the branch.
        """
        if self._config.branch == name:
            panic("Can not delete the current branch")
