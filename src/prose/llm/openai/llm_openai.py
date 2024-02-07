from openai import OpenAI
from prose.domain.code.test import Test

from prose.llm.llm_base import LLMBase
from prose.parser.parser_base import ParserBase
from prose.domain.code.clazz import Class
from prose.domain.code.method import Method

from prose.util.util import panic, retry

OPENAI_ENGINE = "chat_gpt"


class LLMOpenAI(LLMBase):
    def __init__(self, parser: ParserBase):
        self.client = OpenAI()
        self.parser = parser

    def commentify_class(self, clazz: Class) -> None:
        prompt = self.parser.get_prompt_class_comment(clazz)
        if prompt is None:
            return

        while True:
            comment = retry(self._query, prompt)
            if comment is None:
                return panic("I/O Error: Could not retreive OpenAI response, abort!")

            if self.parser.is_valid_class_comment(comment):
                break

        clazz.has_llm_comment = True
        clazz.comment = self.parser.cleanup_class_comment(comment)

    def commentify_method(self, method: Method) -> None:
        prompt = self.parser.get_prompt_method_comment(method)
        if prompt is None:
            return

        while True:
            comment = retry(self._query, prompt)
            if comment is None:
                return panic("I/O Error: Could not retreive OpenAI response, abort!")

            if self.parser.is_valid_method_comment(comment):
                break

        method.has_llm_comment = True
        method.comment = self.parser.cleanup_method_comment(comment)

    def testify_method(self, method: Method) -> None:
        prompt = self.parser.get_prompt_method_tests(method)
        if prompt is None:
            return

        while True:
            tests = retry(self._query, prompt)
            if tests is None:
                return panic("I/O Error: Could not retreive OpenAI response, abort!")

            if self.parser.is_valid_method_tests(tests):
                break

        tests = self.parser.cleanup_method_tests(tests)
        if tests is None:
            return

        method.has_llm_tests = True
        method.tests = [
            Test("\n".join(declaration), decorator + declaration + body)
            for decorator, declaration, body in tests
        ]

    def _query(self, prompt: str, temperature: float = 0) -> str | None:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a programmer to comment and test your code.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content
