import os
import json

import jsbeautifier

from prose.domain.blob.stage import Stage
from prose.util.util import get_digest_object


class StageRepository:

    def __init__(self):
        pass

    def exists(self) -> bool:
        object_path = os.path.join(".prose", "index")
        return os.path.exists(object_path)

    def load(self) -> Stage | None:
        object_path = os.path.join(".prose", "index")
        if os.path.exists(object_path):
            with open(object_path, "r") as f:
                return Stage.of(json.load(f))

    def save(self, content: Stage) -> None:
        object_parent_path = os.path.join(".prose")
        os.makedirs(object_parent_path, exist_ok=True)

        object_path = os.path.join(object_parent_path, "index")
        with open(object_path, "w") as f:
            f.write(
                jsbeautifier.beautify(json.dumps(content.asdict()))
            )
