import os

from typing import Callable

import openai

from prose.llm.llm_base import LLMBase
from prose.parser.code import Code
from prose.domain.clazz import Class
from prose.domain.method import Method
from prose.parser.parser_java import JAVA_DOC_FRAMEWORK, JAVA_TEST_FRAMEWORK
from prose.util.util import panic, retry

OPENAI_ENGINE = "chat_gpt"

PROMPT_DOCUMENT_CLASS = f"""
Comment the class by summarizing the {JAVA_DOC_FRAMEWORK} comments below.
Do not include too much details.
Do not include any parameters or return.
Do not include the class definition.
The final output must be a {JAVA_DOC_FRAMEWORK} comment.
"""

PROMPT_DOCUMENT_METHOD = f"""
Comment the function below using {JAVA_DOC_FRAMEWORK} and by summarizing what the method do, not as steps but as a text.
Include always the list of parameters and return value at the end of the comment.
Do not put the comments in the method body but only in the {JAVA_DOC_FRAMEWORK} section.
Do not include the function body in the response.
The final output must be a valid {JAVA_DOC_FRAMEWORK} comment.
"""

PROMPT_UNIT_TEST = f"""
Generate unit tests for the function below using {JAVA_TEST_FRAMEWORK} framework.
Extract all generated methods and remove everything else.
Do not include the import and class definition.
"""


class LLMOpenAI(LLMBase):
    def __init__(self):
        openai.api_type = "azure"
        openai.api_base = "https://openaidafa.openai.azure.com/"
        openai.api_version = "2023-07-01-preview"
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def commentify_class(
        self,
        clazz: Class,
        methods: list[Method],
        filter: Callable[[str], str] | None = None,
    ) -> None:
        prompt = "\n".join(
            [PROMPT_DOCUMENT_CLASS, "Class: " + clazz.name, ""]
            + ["\n".join(method.comment or []) + "\n" for method in methods]
        )

        content = retry(self._query, prompt)
        if content is None:
            return panic("I/O Error: Could not retreive OpenAI response, abort!")

        if filter is not None:
            content = filter(content)
        clazz.comment = content.splitlines()
        clazz.status = "new"

    def commentify_method(
        self, code: Code, method: Method, filter: Callable[[str], str] | None = None
    ) -> None:
        prompt = "\n".join(
            [
                PROMPT_DOCUMENT_METHOD,
                code.get_block_between(method.start_point, method.end_point),
            ]
        )

        content = retry(self._query, prompt)
        if content is None:
            return panic("I/O Error: Could not retreive OpenAI response, abort!")

        if filter is not None:
            content = filter(content)

        method.comment = content.splitlines()
        method.status = "new"

    def testify_method(
        self, code: Code, method: Method, filter: Callable[[str], str] | None = None
    ) -> None:
        prompt = "\n".join(
            [
                PROMPT_UNIT_TEST,
                code.get_block_between(method.start_point, method.end_point),
            ]
        )

        content = retry(self._query, prompt)
        if content is None:
            return panic("I/O Error: Could not retreive OpenAI response, abort!")

        if filter is not None:
            content = filter(content)

        method.test = content.splitlines()
        method.status = "new"

    def _query(self, prompt: str, temperature: float = 0) -> str | None:
        response = openai.ChatCompletion.create(
            engine=OPENAI_ENGINE,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
        )
        return response["choices"][0]["message"]["content"]  # type: ignore
