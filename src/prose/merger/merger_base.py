from prose.domain.code.file import File
from prose.parser.code import Code


class MergerBase:
    def merge_code(self, code: Code, file: File) -> None:
        pass

    def merge_test(self, code: Code, file: File) -> None:
        pass
