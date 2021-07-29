from unittest import TestCase
from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.ast import (
    Expression,
    Identifier,
    Program,
    LetStatement,
    ReturnStatement,
    ExpressionStatement,
    Integer,
    Prefix,
    Infix,
    Boolean,
    If,
    Block,
    Function,
    Call,
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

    def test_integer_expressions(self) -> None:
        source = '5;'
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._test_program_statements(parser, program)

        expression_statement = cast(ExpressionStatement, program.statements[0])

        assert expression_statement.expression is not None
        self._test_literal_expression(expression_statement.expression, 5)

    def test_prefix_expression(self) -> None:
        source = '!5; -15; !verdadero; !falso'
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()

        self._test_program_statements(parser, program, 4)

        for statemet, (exprected_operator, expected_value) in zip(
            program.statements,
            [('!', 5), ('-', 15), ('!', True), ('!', False)]
        ):
            statemet = cast(ExpressionStatement, statemet)
            self.assertIsInstance(statemet.expression, Prefix)

            prefix = cast(Prefix, statemet.expression)
            self.assertEqual(prefix.operator, exprected_operator)
            
            assert prefix.right is not None
            self._test_literal_expression(prefix.right, expected_value)

    def test_infix_expression(self) -> None:
        source = '''
            5 + 5;
            5 - 5;
            5 * 5;
            5 / 5;
            5 > 5;
            5 < 5;
            5 == 5;
            5 != 5;
            verdadero == falso;
            falso != verdadero;
        '''
        lexer = Lexer(source)
        parser = Parser(lexer)

        program = parser.parse_program()
        self._test_program_statements(parser, program, 10)

        expected_operators_and_values: list[tuple[int, str, int]] = [
            (5, '+', 5),
            (5, '-', 5),
            (5, '*', 5),
            (5, '/', 5),
            (5, '>', 5),
            (5, '<', 5),
            (5, '==', 5),
            (5, '!=', 5),
            (True, '==', False),
            (False, '!=', True),
        ]

        for statemet, (expected_left, expected_operator, expected_right) in zip(
            program.statements,
            expected_operators_and_values
        ):
            statemet = cast(ExpressionStatement, statemet)
            self.assertIsInstance(statemet.expression, Infix)
            self._test_infix_expression(
                statemet.expression,
                expected_left,
                expected_operator,
                expected_right,
            )

    def test_boolean_expression(self) -> None:
        source = 'verdadero; falso;'
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        self._test_program_statements(parser, program, 2)

        expected_values = [True, False]
        for statemet, expected_value in zip(
            program.statements,
            expected_values
        ):
            statemet = cast(ExpressionStatement, statemet)

            assert statemet.expression is not None
            self._test_literal_expression(
                statemet.expression,
                expected_value,
            )
        
    def test_operator_precedence(self) -> None:
        test_sources: list[tuple[str, str, int]] = [
            # Normal order
            ('-a * b;', '((-a) * b)', 1),
            ('!-a;', '(!(-a))', 1),
            ('a + b / c;', '(a + (b / c))', 1),
            (' 3 + 4; -5 * 5;', '(3 + 4)((-5) * 5)', 2),
            ('a + b * c;', '(a + (b * c))', 1),
            ('!a * b;', '((!a) * b)', 1),
            ('verdadero;', 'verdadero', 1),
            ('falso;', 'falso', 1),
            ('a + b * c + d / e - f;', '(((a + (b * c)) + (d / e)) - f)', 1),
            ('5 > 4 == 3 < 4;', '((5 > 4) == (3 < 4))', 1),
            ('3 - 4 * 5 == 3 * 1 + 4 * 5;', '((3 - (4 * 5)) == ((3 * 1) + (4 * 5)))', 1),
            ('3 > 5 == verdadero;', '((3 > 5) == verdadero)', 1),
            ('3 < 5 == falso;', '((3 < 5) == falso)', 1),

            # Using parenthesis
            ('1 + (2 + 3);', '(1 + (2 + 3))', 1),
            ('(5 + 5) * 2;', '((5 + 5) * 2)', 1),
            ('2 / (5 + 5)', '(2 / (5 + 5))', 1),
            ('-(5 + 5)', '(-(5 + 5))', 1),

            # Using function calls
            ('a + suma(b * c) + d;', '((a + suma((b * c))) + d)', 1),
            (
                'suma(a, b, 1, 2 * 3, 4 + 5, suma(6, 7 * 8));',
                'suma(a, b, 1, (2 * 3), (4 + 5), suma(6, (7 * 8)))',
                1
            ),
            (
                'suma(a + b + c * d / f + g);',
                'suma((((a + b) + ((c * d) / f)) + g))',
                1
            ),
            ('abs(-5);', 'abs((-5))', 1),
        ]
        for source, expected_result, expected_statement_count in test_sources:
            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            self._test_program_statements(parser, program, expected_statement_count)
            self.assertEqual(str(program), expected_result)

    def test_if_expression(self) -> None:
        source = 'si (x < y) { z }'
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        self._test_program_statements(parser, program)

        if_expression = cast(
            If,
            cast(
                ExpressionStatement,
                program.statements[0]
            ).expression
        )
        self.assertIsInstance(if_expression, If)

        # Test condition
        assert if_expression.condition is not None
        self._test_infix_expression(if_expression.condition, 'x', '<', 'y')

        # Test consequence
        assert if_expression.consequence is not None
        self.assertIsInstance(if_expression.consequence, Block)
        self.assertEqual(len(if_expression.consequence.statements), 1)

        consequence_statement = cast(
            ExpressionStatement,
            if_expression.consequence.statements[0]
        )
        assert consequence_statement.expression is not None
        self._test_indentifier(consequence_statement.expression, 'z')

        # Test alternative
        self.assertIsNone(if_expression.alternative)

    def test_if_else_expression(self) -> None:
        source = 'si (x != y) { x } si_no { y }'
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        if_expression = cast(
            If,
            cast(
                ExpressionStatement,
                program.statements[0]
            ).expression
        )
        self.assertIsInstance(if_expression, If)

        # Test condition
        assert if_expression.condition is not None
        self._test_infix_expression(if_expression.condition, 'x', '!=', 'y')

        # Test consequence
        assert if_expression.consequence is not None
        self.assertIsInstance(if_expression.consequence, Block)
        self.assertEqual(len(if_expression.consequence.statements), 1)

        consequence_statement = cast(
            ExpressionStatement,
            if_expression.consequence.statements[0]
        )
        assert consequence_statement.expression is not None
        self._test_indentifier(consequence_statement.expression, 'x')

        # Test alternative
        assert if_expression.alternative is not None
        self.assertIsInstance(if_expression.alternative, Block)
        self.assertEqual(len(if_expression.alternative.statements), 1)

        alternative_statement = cast(
            ExpressionStatement,
            if_expression.alternative.statements[0]
        )
        assert alternative_statement.expression is not None
        self._test_indentifier(alternative_statement.expression, 'y')

    def test_function_literal(self) -> None:
        source = 'procedimiento (x, y) { x + y }'
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        self._test_program_statements(parser, program)

        function_literal = cast(
            Function,
            cast(
                ExpressionStatement,
                program.statements[0]
            ).expression
        )
        self.assertIsInstance(function_literal, Function)

        self.assertEqual(len(function_literal.parameters), 2)
        self._test_literal_expression(
            function_literal.parameters[0],
            'x',
        )
        self._test_literal_expression(
            function_literal.parameters[1],
            'y',
        )

        assert function_literal.body is not None
        self.assertEqual(len(function_literal.body.statements), 1)

        body_statement = cast(
            ExpressionStatement,
            function_literal.body.statements[0]
        )
        assert body_statement.expression is not None
        self._test_infix_expression(
            body_statement.expression,
            'x',
            '+',
            'y',
        )

    def test_function_parameters(self) -> None:
        tests: list[tuple[str, list[str]]] =  [
            (
                'procedimiento() {};',
                []
            ),
            (
                'procedimiento(x) {};',
                ['x']
            ),
            (
                'procedimiento(x, y, z) {};',
                ['x', 'y', 'z']
            ),
        ]

        for source, expected_params in tests:
            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            function_literal = cast(
                Function,
                cast(
                    ExpressionStatement,
                    program.statements[0]
                ).expression
            )
            self.assertIsInstance(function_literal, Function)
            self.assertEqual(len(function_literal.parameters), len(expected_params))
            for expected_param, actual_param in zip(
                expected_params,
                function_literal.parameters
            ):
                self._test_literal_expression(actual_param, expected_param)

    def test_call_expression(self) -> None:
        source = 'suma(1, 2 * 3, 4 + 5)'
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        self._test_program_statements(parser, program)
        call_expression = cast(
            Call,
            cast(
                ExpressionStatement,
                program.statements[0]
            ).expression
        )
        self.assertIsInstance(call_expression, Call)

        self._test_indentifier(call_expression.function, 'suma')

        self.assertEqual(len(call_expression.arguments), 3)

        assert call_expression.arguments is not None
        self.assertEqual(len(call_expression.arguments), 3)
        self._test_literal_expression(call_expression.arguments[0], 1)
        self._test_infix_expression(
            call_expression.arguments[1],
            2,
            '*',
            3,
        )
        self._test_infix_expression(
            call_expression.arguments[2],
            4,
            '+',
            5,
        )

    def _test_program_statements(
        self,
        parser: Parser,
        program: Program,
        expected_statement_count: int = 1
    ) -> None:
        if parser.errors:
            print(parser.errors)

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
        elif value_type == int:
            self._test_integer(expression, expected_value)
        elif value_type == bool:
            self._test_boolean(expression, expected_value)
        else:
            self.fail(f'Unhandled type of expression. Got={value_type}')

    def _test_indentifier(self, expression: Expression, expected_value: str) -> None:
        self.assertIsInstance(expression, Identifier)
        identifier = cast(Identifier, expression)
        self.assertEqual(identifier.value, expected_value)
        self.assertEqual(identifier.token.literal, expected_value)

    def _test_integer(self, expression: Expression, expected_value: int) -> None:
        self.assertIsInstance(expression, Integer)
        integer = cast(Integer, expression)
        self.assertEqual(integer.value, expected_value)
        self.assertEqual(integer.token.literal, str(expected_value))

    def _test_infix_expression(
        self,
        expression: Expression,
        expected_left: Any,
        expected_operator: str,
        expected_right: Any
    ) -> None:
        infix = cast(Infix, expression)
        assert infix.left is not None
        self._test_literal_expression(infix.left, expected_left)

        self.assertEqual(infix.operator, expected_operator)

        assert infix.right is not None
        self._test_literal_expression(infix.right, expected_right)

    def _test_boolean(self, expression: Expression, expected_value: bool) -> None:
        self.assertIsInstance(expression, Boolean)
        boolean = cast(Boolean, expression)
        self.assertEqual(boolean.value, expected_value)
        self.assertEqual(boolean.token.literal, 'verdadero' if expected_value else 'falso')
