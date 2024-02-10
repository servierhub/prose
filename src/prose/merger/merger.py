class Merger:

    def __init__(self, path_or_lines: str | list[str]):
        self.modified = False
        if isinstance(path_or_lines, str):
            with open(path_or_lines, "r") as f:
                self.src_lines = f.readlines()
        else:
            self.src_lines = path_or_lines

        self.mapper = {}
        for i in range(0, len(self.src_lines)):
            self.mapper[i] = i

        self.num = len(self.src_lines)

    def is_modified(self):
        return self.modified

    def get_num(self):
        return self.num

    def get_text(self):
        return "".join(self.src_lines)

    def find(self, text: str) -> tuple[int, int] | None:
        num_line = 0
        for line in self.src_lines:
            if text in line:
                return (num_line, line.find(text))
            num_line += 1

    def find_last(self, text: str) -> tuple[int, int] | None:
        num_line = self.num - 1
        for line in reversed(self.src_lines):
            if text in line:
                return (num_line, line.find(text))
            num_line -= 1

    def merge(self, start_point: tuple[int, int], text: list[str]) -> None:
        line_num = start_point[0]
        spaces = " " * start_point[1]
        for line in text:
            self.src_lines.insert(self.mapper[line_num], spaces + line + "\n")
            for k, v in self.mapper.items():
                if k >= line_num:
                    self.mapper[k] = v + 1
        self.modified = True


