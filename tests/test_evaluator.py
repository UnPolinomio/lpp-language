from unittest import TestCase
from typing import cast

from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.object import (
    Object,
    Integer,
)
from lpp.evaluator import evaluate

class EvaluatorTest(TestCase):
    def test_integer_evaluation(self) -> None:
        tests: list[tuple[str, int]] = [
            ('5', 5),
            ('10', 10),
        ]

        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def _evaluate_tests(self, source: str) -> Object:
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        evaluated = evaluate(program)

        assert evaluated is not None
        return evaluated

    def _test_integer_object(self, evaluated: Object, expected: int) -> None:
        self.assertIsInstance(evaluated, Integer)
        evaluated = cast(Integer, evaluated)

        self.assertEqual(evaluated.value, expected)
