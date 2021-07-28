from unittest import TestCase
from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.ast import (
    Expression,
    Identifier,
    Program,
    LetStatement,
    ReturnStatement,
    ExpressionStatement
)

from typing import Any, cast, Type

class ParserTest(TestCase):
    def test_parse_program(self) -> None:
        source: str = 'variable x = 5;'
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()

        self.assertIsNotNone(program)
        self.assertIsInstance(program, Program)

    def test_let_statements(self) -> None:
        source = '''
            variable x = 5;
            variable y = 10;
            variable foo = 20;
        '''
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()

        self.assertEqual(len(program.statements), 3)

        for statement in program.statements:
            self.assertEqual(statement.token_literal(), 'variable')
            self.assertIsInstance(statement, LetStatement)

    def test_names_in_let_statement(self) -> None:
        source = '''
            variable x = 5;
            variable y = 10;
            variable foo = 20;
        '''
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()

        names: list[str] = []
        for statement in program.statements:
            statement = cast(LetStatement, statement)

            identifier = statement.name
            self.assertIsNotNone(identifier)

            names.append(identifier.value)

        self.assertEqual(names, ['x', 'y', 'foo'])

    def test_parse_errors(self) -> None:
        source = 'variable x 5;'
        lexer = Lexer(source)
        parser = Parser(lexer)

        parser.parse_program()

        self.assertEqual(len(parser.errors), 1)

    def test_return_statement(self) -> None:
        source = '''
            regresa 5;
            regresa foo;
        '''

        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        self.assertEqual(len(program.statements), 2)
        for statement in program.statements:
            self.assertEqual(statement.token_literal(), 'regresa')
            self.assertIsInstance(statement, ReturnStatement)

    def test_identifier_expression(self) -> None:
        source = 'foobar;'
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()

        self._test_program_statements(parser, program)

        expression_statement = cast(ExpressionStatement, program.statements[0])

        assert expression_statement.expression is not None
        self._test_literal_expression(expression_statement.expression, 'foobar')


    def _test_program_statements(
        self,
        parser: Parser,
        program: Program,
        expected_statement_count: int = 1
    ) -> None:
        self.assertEqual(len(parser.errors), 0)
        self.assertEqual(len(program.statements), expected_statement_count)
        self.assertIsInstance(program.statements[0], ExpressionStatement)


    def _test_literal_expression(
        self,
        expression: Expression,
        expected_value: Any
    ) -> None:
        value_type: Type = type(expected_value)

        if value_type == str:
            self._test_indentifier(expression, expected_value)

        else:
            self.fail(f'Unhandled type of expression. Got={value_type}')

    def _test_indentifier(self, expression: Expression, expected_value: str) -> None:
        self.assertIsInstance(expression, Identifier)
        identifier = cast(Identifier, expression)
        self.assertEqual(identifier.value, expected_value)
        self.assertEqual(identifier.token.literal, expected_value)
