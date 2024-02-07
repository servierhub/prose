import os
import json

import jsbeautifier

from prose.domain.blob.tree import Tree
from prose.util.util import get_digest_string


class BlobRepository:

    def __init__(self):
        pass

    def exists(self, digest: str) -> bool:
        object_path = os.path.join(".prose", "objects", digest[:2], digest)
        return os.path.exists(object_path)

    def load(self, digest: str) -> str | None:
        object_path = os.path.join(".prose", "objects", digest[:2], digest)
        if os.path.exists(object_path):
            with open(object_path, "r") as f:
                return f.read()

    def save(self, content: str, digest: str | None = None) -> str:
        if digest is None:
            digest = get_digest_string(content)

        object_parent_path = os.path.join(".prose", "objects", digest[:2])
        os.makedirs(object_parent_path, exist_ok=True)

        object_path = os.path.join(object_parent_path, digest)
        if not os.path.exists(object_path):
            with open(object_path, "w") as f:
                f.write(content)

        return digest
