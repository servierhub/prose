import os
import json

import jsbeautifier

from prose.domain.blob.config import Config
from prose.util.util import get_digest_object


class ConfigRepository:

    def __init__(self):
        pass

    def exists(self) -> bool:
        object_path = os.path.join(".prose", "config")
        return os.path.exists(object_path)

    def load(self) -> Config | None:
        object_path = os.path.join(".prose", "config")
        if os.path.exists(object_path):
            with open(object_path, "r") as f:
                return Config.of(json.load(f))

    def save(self, content: Config) -> None:
        object_parent_path = os.path.join(".prose")
        os.makedirs(object_parent_path, exist_ok=True)

        object_path = os.path.join(object_parent_path, "config")
        if not os.path.exists(object_path):
            with open(object_path, "w") as f:
                f.write(
                    jsbeautifier.beautify(json.dumps(content.asdict()))
                )
