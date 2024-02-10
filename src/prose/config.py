from prose.dao.blob.config_repository import ConfigRepository
from prose.domain.blob.config import Config


class ConfigOp:

    def __init__(self, config: Config):
        self._config = config
        self._config_repo = ConfigRepository()

    def set_base_path(self, base_path: str):
        """Set the base path.
        """
        self._config.base_path = base_path
        self._config_repo.save(self._config)
