from io import StringIO

from prose.domain.file import File

class Code:
    def __init__(self, file: File):
        self.file = file
        self.src_lines = None

    def load(self) -> bool:
        try:
            with open(self.file.path, "r") as f:
                self.src_lines = f.readlines()
                return True
        except IOError:
            return False

    def get_str_at(self, point: (int)) -> str:
        row, column = point
        if row >= len(self.src_lines) or column >= len(self.src_lines[row]):
            return None
        return self.src_lines[row][column:]

    def get_str_between(self, start_point: (int), end_point: (int)) -> str:
        row, start_column = start_point
        _, end_column = end_point
        if row >= len(self.src_lines) or start_column >= len(self.src_lines[row]):
            return None
        return self.src_lines[row][start_column:end_column]

    def get_bytes_at(self, point: (int)) -> bytes:
        c = self.get_str_at(point)
        return c.encode("utf8") if c != None else None

    def get_block_between(
        self, start_point: (int), end_point: (int), show_line_numbers=True
    ) -> str:
        start_y, _ = start_point
        end_y, _ = end_point
        with StringIO() as buffer:
            for y in range(start_y, end_y + 1):
                if show_line_numbers:
                    buffer.write(str(y).rjust(3, "0"))
                    buffer.write(" ")
                buffer.write(self.get_str_at((y, 0)))
            return buffer.getvalue()
