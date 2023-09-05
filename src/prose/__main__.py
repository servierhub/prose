import re
import sys

from prose.llm.llm import LLM, PROMPT_DOCUMENT_CLASS
from prose.domain.file import File
from prose.dao.file_repository import FileRepository
from prose.parser.code import Code
from prose.parser.parser_java import ParserJava

class App:
    def __init__(self):
        self.file_repo = FileRepository()
        self.parser = ParserJava()
        self.llm = LLM()

    def main(self):
        self.file_repo.load("prose.json")

        file = self.file_repo.find("helloworld.java")
        if file is None:
            file = File.of("data/helloworld.java")

        code = Code(file)
        if not code.load():
            print(f"I/O Error: could not load the file '{file.path}'")
            sys.exit()
        self.parser.parse(code)

        for method in file.methods:
            if method.comment is None:
                self.llm.commentify_method(code, method)
            if method.test is None:
                self.llm.testify_method(code, method, filter=lambda s: re.sub(r"```.*\n?", "", s))

        if file.clazz.comment is None:
            self.llm.commentify_class(file.clazz, file.methods)

        self.file_repo.upsert(file)
        self.file_repo.save("prose.json")


if __name__ == "__main__":
    app = App()
    app.main()
