from prose.dao.file_repository import FileRepository
from prose.domain.commit_object import CommitObject
from prose.domain.prose_object import ProseObject

class TreeWalver:
    def __init__(self):
        self.file_repo = FileRepository()

    def cat(self, digest: str) -> None:
        print(self.file_repo.load_blob(digest, "str"))

    def walk(self) -> str | None:
        ref = self.file_repo.load_ref("main")
        if ref is not None:
            print("commit", ref)
            print()
            commit: CommitObject = self.file_repo.load_blob(ref, "commit") # type: ignore
            root = self.file_repo.load_blob(commit.tree, "list")
            self._walk_rec(root)  # type: ignore

    def _walk_rec(self, tree: list[ProseObject]) -> None:
        for node in tree:
            if node.type == "tree":
                self._walk_rec(self.file_repo.load_blob(node.digest, "list")) # type: ignore
            elif node.type == "file":
                methods: list[ProseObject] = self.file_repo.load_blob(node.digest, "list") # type: ignore
                for method in methods:
                    comments_or_tests: list[ProseObject] = self.file_repo.load_blob(method.digest, "list") # type: ignore
                    for comment_or_test in comments_or_tests:
                        print(comment_or_test.type, comment_or_test.digest)
                        print(f"Signature: {comment_or_test.name}")
                        print()
                        print(self.file_repo.load_blob(comment_or_test.digest, "str"))
                        print()

