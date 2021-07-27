from unittest import TestCase
from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.ast import Program, LetStatement, ReturnStatement

from typing import cast

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
