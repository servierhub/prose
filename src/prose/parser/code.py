from io import StringIO

from prose.domain.file import File
from prose.util.util import panic


class Code:
    def __init__(self, file: File):
        self.file = file
        self.src_lines: list[str] | None = None

    def load(self) -> None:
        try:
            with open(self.file.path, "r") as f:
                self.src_lines = f.readlines()
        except IOError:
            panic(f"I/O Error: could not load the file '{self.file.path}'")

    def get_str_at(self, point: tuple[int, int]) -> str | None:
        if self.src_lines is None:
            return None
        row, column = point
        if row >= len(self.src_lines) or column >= len(self.src_lines[row]):
            return None
        return self.src_lines[row][column:]

    def get_str_between(
        self, start_point: tuple[int, int], end_point: tuple[int, int]
    ) -> str | None:
        if self.src_lines is None:
            return None
        row, start_column = start_point
        _, end_column = end_point
        if row >= len(self.src_lines) or start_column >= len(self.src_lines[row]):
            return None
        return self.src_lines[row][start_column:end_column]

    def get_bytes_at(self, point: tuple[int, int]) -> bytes | None:
        c = self.get_str_at(point)
        return c.encode("utf8") if c != None else None

    def get_block_between(
        self,
        start_point: tuple[int, int],
        end_point: tuple[int, int],
        show_line_numbers=False
    ) -> str:
        start_y, start_x = start_point
        end_y, end_x = end_point

        if start_y == end_y:
            line = self.get_str_at((start_y, 0)) or ""
            return line[start_x:end_x]

        with StringIO() as buffer:
            for y in range(start_y, end_y + 1):
                line = self.get_str_at((y, 0)) or ""
                if show_line_numbers:
                    buffer.write(str(y).rjust(3, "0"))
                    buffer.write(" ")
                if y == start_y:
                    buffer.write(line[start_x:])
                elif y == end_y:
                    buffer.write(line[:end_x])
                else:
                    buffer.write(line)
            return buffer.getvalue()
