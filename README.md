# Prose

![Servier Inspired](https://raw.githubusercontent.com/servierhub/servierhub-charter/main/badges/inspired.svg)

A developer tool to bring the power of LLM to the CI/CD by ensuring documentation and unit tests for an entire source
tree.

## Intro

Prose is a tool to document and generate tests for Java and Python projects using LLM. It allows for easy addition of
new languages and LLM systems, such as Azure OpenAI (as the default). Prose parses source code and generates comments
and tests incrementally. Prose can also be integrated into a CI/CD pipeline and halt if there are classes or methods
without documentation or tests. Additionally, Prose collects all information and adds a summary to the README file.

## Feature overview

-   Support OpenAI
    -   Documentation: OK
    -   Test generation: OK
-   Support Java
    -   Documentation: OK (JAVADOC)
    -   Test generation: In progress (JUNIT)
-   Support Python
    -   Documentation: TBD
    -   Test generation: TBD
-   Support Behave
    -   Test generation: TBD
-   Support Poetry
    -   Documentation: TBD
-   Support Maven
    -   Documentation: TBD

## How does it work?

Prose works in 3 steps:

-   Step 1: Prose parses a tree source, collects non documented classes and methods and proposes comments and tests using
    LLM. The sources are not modified.

-   Step 2: The developer checks the propositions and amends them.

-   Step 3: Prose merge the comments and the tests.

## Getting Started

Initialization

```bash
prose config set-base-path src
```

Step 1 - Generate the prose.json collecting classes and methods within the src folder and documenting them

```bash
prose add .
```

Step 2 - Review the propositions

```bash
prose status
```

Compare to an original file

```bash
prose diff <blob_id>
```

Step 3 - Merge the final comments and tests in place

```bash
prose commit --merge
```

Branch management

Create or switch to a branch

```bash
prose branch checkout <branch_name>
```

Print the current branch

```bash
prose branch show
```

### Requirements

TBD by Prose

### Install

Use git to clone this repository into your computer.

```bash
git clone https://gitlab.com/romualdrousseau/prose.git
```

### Testing

TBD by Prose

## Contribute

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

TBD

## Conclusion

TBD
