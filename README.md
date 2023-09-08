# Prose

A developer tool to bring the power of LLM to the CI/CD by ensuring documentation and unit tests for an entire source
tree.

## Intro

Prose is a tool to document and generate tests for Java and Python projects using LLM. It allows for easy addition of
new languages and LLM systems, such as Azure OpenAI (as the default). Prose parses source code and generates comments
and tests incrementally. Prose can also be integrated into a CI/CD pipeline and halt if there are classes or methods
without documentation or tests. Additionally, Prose collects all information and adds a summary to the README file.

## Feature overview

- Support OpenAI
    - Documentation: OK
    - Test generation: OK
- Support Java
    - Documentation: OK (JAVADOC)
    - Test generation: In progress (JUNIT)
- Support Python
    - Documentation: TBD
    - Test generation: TBD
- Support Behave
    - Test generation: TBD
- Support Poetry
    - Documentation: TBD
- Support Maven
     - Documentation: TBD

## How does it work?

Prose works in 3 steps:

- Step 1: Prose parses a tree source, collects non documented classes and methods and proposes comments and tests using
LLM. The sources are not modified. The comments and tests are saved in a prose.json file with a status "new".
If any "new" are found, Prose warns the developper and terminates in error, otherwise, terminates without error silently.

- Step 2: the developer checks the prose.json for status "new", check and corrects the proposed comments and tests and
then change the status as "final".

- Step 3: the tool reruns in merge mode all comments and tests marked "final".

## Getting Started

Step 1 - Generate the prose.json collecting classes and methods within the src folder and documenting them

```bash
prose --generate src
```

Step 2 - Review the prose.json with your favorite editor

```json
[
    {
        "name": "helloworld.java",
        "path": "data/helloworld.java",
        "clazz": {
            "name": "helloworld",
            "start_point": [2, 0],
            "end_point": [15, 1],
            "comment": [
                "/**",
                " * This class contains a method that takes two integers as parameters and returns their sum.",
                " * The main method checks if the value of x is equal to the result of the add method with parameters 1 and 0.",
                " * If the condition is true, it prints \"Hello the world\".",
                " * After that, it always prints \"Hello the world\".",
                " * The main method does not have any return value.",
                " * It takes an array of strings representing command line arguments as a parameter.",
                " */"
            ],
            "status": "review"
        },
        "methods": [
            {
                "name": "add",
                "start_point": [4, 4],
                "end_point": [6, 5],
                "comment": [
                    "/**",
                    " * This method takes two integers as parameters and returns the sum of the two integers.",
                    " *",
                    " * @param x the first integer",
                    " * @param y the second integer",
                    " * @return the sum of x and y",
                    " */"
                ],
                "test": [
                    "@Test",
                    "public void testAddPositiveNumbers() {",
                    "    int result = add(5, 10);",
                    "    assertEquals(15, result);",
                    "}",
                    "",
                    "@Test",
                    "public void testAddNegativeNumbers() {",
                    "    int result = add(-5, -10);",
                    "    assertEquals(-15, result);",
                    "}",
                    "",
                    "@Test",
                    "public void testAddZeroToNumber() {",
                    "    int result = add(0, 10);",
                    "    assertEquals(10, result);",
                    "}",
                    "",
                    "@Test",
                    "public void testAddNumberToZero() {",
                    "    int result = add(5, 0);",
                    "    assertEquals(5, result);",
                    "}",
                    "",
                    "@Test",
                    "public void testAddZeroToZero() {",
                    "    int result = add(0, 0);",
                    "    assertEquals(0, result);",
                    "}"
                ],
                "status": "review"
            },
            {
                "name": "main",
                "start_point": [8, 4],
                "end_point": [14, 5],
                "comment": [
                    "/**",
                    " * The main method checks if the value of x is equal to the result of the add method with parameters 1 and 0.",
                    " * If the condition is true, it prints \"Hello the world\".",
                    " * After that, it always prints \"Hello the world\".",
                    " * ",
                    " * Parameters:",
                    " * - args: an array of strings representing command line arguments",
                    " * ",
                    " * Return value: none",
                    " */"
                ],
                "test": [
                    "@Test",
                    "public void testMain() {",
                    "    // Test case 1",
                    "    ByteArrayOutputStream outContent = new ByteArrayOutputStream();",
                    "    System.setOut(new PrintStream(outContent));",
                    "    String expectedOutput1 = \"Hello the world\\n\";",
                    "    Main.main(new String[]{});",
                    "    assertEquals(expectedOutput1, outContent.toString());",
                    "",
                    "    // Test case 2",
                    "    outContent.reset();",
                    "    String expectedOutput2 = \"Hello the world\\n\";",
                    "    Main.main(new String[]{\"arg1\", \"arg2\"});",
                    "    assertEquals(expectedOutput2, outContent.toString());",
                    "}",
                    "",
                    "@Test",
                    "public void testAdd() {",
                    "    // Test case 1",
                    "    int result1 = Main.add(1, 0);",
                    "    assertEquals(1, result1);",
                    "",
                    "    // Test case 2",
                    "    int result2 = Main.add(5, -3);",
                    "    assertEquals(2, result2);",
                    "",
                    "    // Test case 3",
                    "    int result3 = Main.add(-10, -5);",
                    "    assertEquals(-15, result3);",
                    "}"
                ],
                "status": "review"
            }
        ]
    }
]
```

Step 3 - Merge the final comments and tests in place (of a folder can be given to copy the source tree)

```bash
prose --merge --inplace
```

### Requirements

TBD by Prose

### Install

Use git to clone this repository into your computer.

```
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

