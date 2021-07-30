from unittest import TestCase
from typing import cast

from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.object import (
    Object,
    Integer,
    Boolean,
)
from lpp.evaluator import evaluate

class EvaluatorTest(TestCase):
    def test_integer_evaluation(self) -> None:
        tests: list[tuple[str, int]] = [
            ('5', 5),
            ('10', 10),
            ('-5', -5),
            ('-10', -10),
            ('5 + 5', 10),
            ('5 - 10', -5),
            ('2 * 2 * 2 * 2', 16),
            ('2 * 5 - 3', 7), 
            ('50 / 2', 25),
            ('2 * (5 - 3)', 4),
            ('(2 + 7) / 3', 3),
            (' 50 / 2 * 2 + 10', 60),
            ('5 / 2', 2),
        ]

        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)
    
    def test_boolean_expression(self) -> None:
        tests: list[tuple[str, bool]] = [
            ('verdadero', True),
            ('falso', False),
            ('1 < 2', True),
            ('1 > 2', False),
            ('1 == 2', False),
            ('1 == 1', True),
            ('1 != 2', True),
            ('1 != 1', False),
            ('verdadero == verdadero', True),
            ('falso == falso', True),
            ('verdadero != verdadero', False),
            ('falso != falso', False),
            ('(1 < 2) == verdadero', True),
            ('(1 < 2) == falso', False),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

    def test_bang_operator(self) -> None:
        tests: list[tuple[str, bool]] = [
            ('!verdadero', False),
            ('!falso', True),
            ('!!verdadero', True),
            ('!!falso', False),
            ('!5', False),
            ('!!5', True),
        ]

        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

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

    def _test_boolean_object(self, evaluated: Object, expected: bool) -> None:
        self.assertIsInstance(evaluated, Boolean)
        evaluated = cast(Boolean, evaluated)

        self.assertEqual(evaluated.value, expected)
