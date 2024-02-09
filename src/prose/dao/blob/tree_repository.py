import os
import json

import jsbeautifier

from prose.domain.blob.tree import Tree
from prose.util.util import get_digest_object


class TreeRepository:

    def __init__(self):
        pass

    def exists(self, digest: str) -> bool:
        object_path = os.path.join(".prose", "objects", digest[:2], digest)
        return os.path.exists(object_path)

    def load(self, digest: str) -> list[Tree] | None:
        try:
            object_path = os.path.join(".prose", "objects", digest[:2], digest)
            if os.path.exists(object_path):
                with open(object_path, "r") as f:
                    return [Tree.of(x) for x in json.load(f)]
        except:
            return None

    def save(self, content: list[Tree], digest: str | None = None) -> str:
        content_asdicts = [x.asdict() for x in content]

        if digest is None:
            digest = get_digest_object(content_asdicts)

        object_parent_path = os.path.join(".prose", "objects", digest[:2])
        os.makedirs(object_parent_path, exist_ok=True)

        object_path = os.path.join(object_parent_path, digest)
        if not os.path.exists(object_path):
            with open(object_path, "w") as f:
                f.write(
                    jsbeautifier.beautify(json.dumps(content_asdicts))
                )

        return digest
