import os
import json

import jsbeautifier

from prose.domain.file import File


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

    def save_ref(self, name: str, content: str) -> None:
        refs_path = os.path.join(".prose", "refs")
        os.makedirs(refs_path, exist_ok=True)

        ref_main_path = os.path.join(refs_path, name)
        with open(ref_main_path, "w") as f:
            f.write(content)

    def exists_object(self, digest: str) -> bool:
        object_path = os.path.join(".prose", "objects", digest[:2], digest)
        return os.path.exists(object_path)

    def save_object(self, digest: str, content: str | list[str] | dict | list[dict]) -> None:
        object_parent_path = os.path.join(".prose", "objects", digest[:2])
        os.makedirs(object_parent_path, exist_ok=True)

        object_path = os.path.join(object_parent_path, digest)
        if not os.path.exists(object_path):
            with open(object_path, "w") as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    f.write(json.dumps(content, indent=4))

