import os
import json
from typing import Any

import jsbeautifier
from prose.domain.commit_object import CommitObject

from prose.domain.file import File
from prose.domain.prose_object import ProseObject
from prose.util.util import get_digest_object, get_digest_string


class FileRepository:
    Storage = dict[str, File]()

    def __init__(self):
        pass

    def find(self, path: str) -> File | None:
        return FileRepository.Storage.get(path)

    def findall(self) -> list[File]:
        return list(FileRepository.Storage.values())

    def upsert(self, afile: File) -> None:
        FileRepository.Storage[afile.path] = afile

    def delete(self, afile: File) -> None:
        del FileRepository.Storage[afile.path]

    def load(self, file_path: str) -> None:
        tmp = dict[str, File]()

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = []

        for file_data in data:
            file_path = file_data["path"]
            tmp[file_path] = File.of(file_data)

        FileRepository.Storage = tmp

    def save(self, file_path: str) -> None:
        with open(file_path, "w") as f:
            data = json.dumps([x.asdict() for x in FileRepository.Storage.values()])
            f.write(jsbeautifier.beautify(data))

    def load_ref(self, name: str) -> str | None:
        ref_path = os.path.join(".prose", "refs", name)
        with open(ref_path, "r") as f:
            return f.read()

    def save_ref(self, name: str, content: str) -> None:
        refs_path = os.path.join(".prose", "refs")
        os.makedirs(refs_path, exist_ok=True)

        ref_path = os.path.join(refs_path, name)
        with open(ref_path, "w") as f:
            f.write(content)

    def exists_blob(self, digest: str) -> bool:
        object_path = os.path.join(".prose", "objects", digest[:2], digest)
        return os.path.exists(object_path)

    def load_blob(self, digest: str, type: str = "obj") -> str | CommitObject | list[ProseObject] | ProseObject | None:
        object_path = os.path.join(".prose", "objects", digest[:2], digest)
        if os.path.exists(object_path):
            with open(object_path, "r") as f:
                if type == "str":
                    return f.read()
                elif type == "commit":
                    return CommitObject.of(json.load(f))
                elif type == "list":
                    return [ProseObject.of(x) for x in json.load(f)]
                else:
                    return ProseObject.of(json.load(f))

    def save_blob(
        self,
        content: str | CommitObject | list[ProseObject] | ProseObject,
        digest: str | None = None,
    ) -> str:
        if digest is None:
            if isinstance(content, str):
                digest = get_digest_string(content)
            elif isinstance(content, list):
                digest = get_digest_object([x.asdict() for x in content])
            else:
                digest = get_digest_object(content.asdict())

        object_parent_path = os.path.join(".prose", "objects", digest[:2])
        os.makedirs(object_parent_path, exist_ok=True)

        object_path = os.path.join(object_parent_path, digest)
        if not os.path.exists(object_path):
            with open(object_path, "w") as f:
                if isinstance(content, str):
                    f.write(content)
                elif isinstance(content, list):
                    f.write(json.dumps([x.asdict() for x in content], indent=4))
                else:
                    f.write(json.dumps(content.asdict(), indent=4))

        return digest
