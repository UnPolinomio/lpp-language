from unittest import TestCase

from lpp.ast import (
    Identifier,
    LetStatement,
    Program,
    ReturnStatement
)
from lpp.token import (
    Token,
    TokenType
)

class ASTTest(TestCase):
    def test_let_statement(self):
        program = Program(statements=[
            LetStatement(
                token=Token(
                    token_type=TokenType.LET,
                    literal='variable'
                ),
                name=Identifier(
                    token=Token(
                        token_type=TokenType.IDENT,
                        literal='my_var'
                    ),
                    value='mi_var'
                ),
                value=Identifier(
                    token=Token(
                        token_type=TokenType.IDENT,
                        literal='otra_variable'
                    ),
                    value='otra_variable'
                )
            )
        ])

        program_str = str(program)

        self.assertEqual(program_str, 'variable mi_var = otra_variable;')

    def test_return_statement(self) -> None:
        proqram = Program(statements=[
            ReturnStatement(
                token=Token(
                    token_type=TokenType.RETURN,
                    literal='regresa'
                ),
                return_value=Identifier(
                    token=Token(
                        token_type=TokenType.IDENT,
                        literal='mi_var'
                    ),
                    value='mi_var'
                )
            )
        ])
        self.assertEqual(str(proqram), 'regresa mi_var;')
