import fire
import fire.core

from prose.branch import BranchOp
from prose.config import ConfigOp
from prose.default import DefaultOp
from prose.domain.blob.config import Config
from prose.dao.blob.config_repository import ConfigRepository


class Main(DefaultOp):
    """A CLI tool to bring the power of LLM to the CI/CD by ensuring documentation and unit tests for an
    entire source tree.

    Prose is a CLI tool to document and generate tests for Java and Python projects using LLM. It allows for easy addition of
    new languages and LLM systems, such as Azure OpenAI (as the default). Prose parses source code and generates comments
    and tests incrementally. Prose can also be integrated into a CI/CD pipeline and abort if there are classes or methods
    without documentation or tests. Additionally, Prose adds a summary to the README file.
    """

    def __init__(self):
        config_repo = ConfigRepository()
        config = config_repo.load() or Config(".", "main")
        if not config_repo.exists():
            config_repo.save(config)

        super().__init__(config)
        self.config = ConfigOp(config)
        self.branch = BranchOp(config)

if __name__ == "__main__":
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(Main)
