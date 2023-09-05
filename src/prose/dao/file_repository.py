import os
import json
import jsbeautifier

from prose.domain.file import File
from prose.domain.clazz import Class
from prose.domain.method import Method


class FileRepository:
    Storage = dict[str, File]()

    def __init__(self):
        pass

    def find(self, name: str) -> File | None:
        return FileRepository.Storage.get(name)

    def findall(self) -> File:
        return list(FileRepository.Storage.values())

    def upsert(self, afile: File) -> None:
        FileRepository.Storage[afile.name] = afile

    def delete(self, afile: File) -> None:
        del FileRepository.Storage[afile.name]

    def load(self, file_path: str) -> None:
        tmp = dict[str, File]()

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = []

        for file_data in data:
            file_name = file_data["name"]
            tmp[file_name] = File.of(file_data)

        FileRepository.Storage = tmp

    def save(self, file_path: str) -> None:
        with open(file_path, "w") as f:
            data = json.dumps([x.asdict() for x in FileRepository.Storage.values()])
            f.write(jsbeautifier.beautify(data))
