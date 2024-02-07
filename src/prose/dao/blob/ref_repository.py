import os
import json

import jsbeautifier

from prose.domain.blob.tree import Tree
from prose.util.util import get_digest_object


class RefRepository:

    def __init__(self):
        pass

    def load(self, name: str) -> str | None:
        ref_path = os.path.join(".prose", "refs", name)
        with open(ref_path, "r") as f:
            return f.read()

    def save(self, name: str, content: str) -> None:
        refs_path = os.path.join(".prose", "refs")
        os.makedirs(refs_path, exist_ok=True)

        ref_path = os.path.join(refs_path, name)
        with open(ref_path, "w") as f:
            f.write(content)
