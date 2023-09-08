from prose.parser.code import Code


class MergerBase:
    def merge_code(self, code: Code, path: str) -> None:
        pass

    def merge_test(self, code: Code, path: str) -> None:
        pass
