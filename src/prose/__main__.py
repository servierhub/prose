import fire
import fire.core

from prose.core import Prose


class Main:
    """A CLI tool to bring the power of LLM to the CI/CD by ensuring documentation and unit tests for an
    entire source tree.

    Prose is a CLI tool to document and generate tests for Java and Python projects using LLM. It allows for easy addition of
    new languages and LLM systems, such as Azure OpenAI (as the default). Prose parses source code and generates comments
    and tests incrementally. Prose can also be integrated into a CI/CD pipeline and halt if there are classes or methods
    without documentation or tests. Additionally, Prose collects all information and adds a summary to the README file.
    """

    def parse(self) -> None:
        """Parses a tree source, collects non documented classes and methods and proposes comments and tests using LLM."""
        prose = Prose()
        prose.parse()

    def merge(self, inplace: bool = False) -> None:
        """Merges all comments and tests marked "review" into the source code.

        Args:
            inplace (bool): modify the source code in place, otherwise create a copy.
        """
        prose = Prose()
        prose.merge(inplace)


if __name__ == "__main__":
    # fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(Main)
