from prose.merger.merger_base import MergerBase
from prose.domain.file import File
from prose.parser.code import Code


class MergerJava(MergerBase):
    def merge_code(self, code: Code, file: File) -> None:
        if file.clazz is None:
            return

        with open(file.path, "r") as f:
            src_lines = f.readlines()

        if file.clazz.comment is not None and file.clazz.status == "review":
            pos = self._find_code_line(code, file.clazz.start_point, src_lines)
            if pos >= 0:
                self._apply_comment(src_lines, pos, file.clazz.comment)
                file.clazz.status = "final"

        for method in file.methods:
            if method.comment is not None and method.status == "review":
                pos = self._find_code_line(code, method.start_point, src_lines)
                if pos >= 0:
                    self._apply_comment(src_lines, pos, method.comment)
                    method.status = "final"

        with open(file.path, "w") as f:
            f.writelines(src_lines)

    def merge_test(self, code: Code, path: str) -> None:
        pass

    def _find_code_line(
        self, code: Code, start_point: tuple[int, int], src_lines: list[str]
    ) -> int:
        code_line = code.get_str_at((start_point[0], 0))
        if code_line is not None:
            i = 0
            for line in src_lines:
                if code_line.startswith(line):
                    return i
                i += 1
        return -1

    def _apply_comment(
        self, src_lines: list[str], pos: int, comment: list[str]
    ) -> None:
        for line in comment:
            src_lines.insert(pos, "\t" + line + "\n")
            pos += 1
