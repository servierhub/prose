from prose.parser.code import Code
from prose.domain.file import File

class ParserBase:

    def parse(self, code: Code) -> None:
        pass
