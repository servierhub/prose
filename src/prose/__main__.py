import fire
import fire.core

from prose.core import Prose


class Main:
    """A CLI tool to bring the power of LLM to the CI/CD by ensuring documentation and unit tests for an
    entire source tree.

    Prose is a CLI tool to document and generate tests for Java and Python projects using LLM. It allows for easy addition of
    new languages and LLM systems, such as Azure OpenAI (as the default). Prose parses source code and generates comments
    and tests incrementally. Prose can also be integrated into a CI/CD pipeline and abort if there are classes or methods
    without documentation or tests. Additionally, Prose adds a summary to the README file.
    """

    def parse(self, src: str = "src/") -> None:
        """Parses a source tree.

        Prose collects undocumented classes and methods, proposes comments and tests using LLM. Prose aborts if some
        undocumented or untested classes or methods are found.

        Args:
            src (str): the source tree to parse.
        """
        with Prose() as prose:
            prose.parse(src)

    def merge(self, inplace: bool = False) -> None:
        """Merges all comments and tests marked "review".

        Args:
            inplace (bool): Modify the source code in place, otherwise create a copy.
        """
        with Prose() as prose:
            prose.merge(inplace)


if __name__ == "__main__":
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(Main)
