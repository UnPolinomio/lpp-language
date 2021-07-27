from typing import Optional
from typing import Optional

from lpp.ast import Identifier, Program, Statement, LetStatement
from lpp.lexer import Lexer
from lpp.token import Token, TokenType

class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self._lexer = lexer
        self._current_token: Token = lexer.next_token()
        self._peek_token: Token = lexer.next_token()

        self._errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        return self._errors

    def parse_program(self):
        statements=[]

        while self._current_token.token_type != TokenType.EOF:
            statement = self._parse_statement()
            if statement is not None:
                statements.append(statement)
            
            self._advance_token()

        return Program(statements=statements)

    def _advance_token(self) -> None:
        self._current_token = self._peek_token
        self._peek_token = self._lexer.next_token()

    def _expected_token(self, token_type: TokenType) -> bool:
        if self._peek_token.token_type == token_type:
            self._advance_token()
            return True

        self._expected_token_error(token_type)
        return False

    def _expected_token_error(self, token_type: TokenType) -> None:
        error = \
            f'Se esperaba que el siguiente token fuera {token_type} ' \
            f'pero se obtuvo {self._peek_token.token_type}'
        self._errors.append(error)

    def _parse_statement(self) -> Optional[Statement]:
        if self._current_token.token_type == TokenType.LET:
            return self._parse_let_statement()

        return None

    def _parse_let_statement(self) -> Optional[LetStatement]:
        let_token = self._current_token

        if not self._expected_token(TokenType.IDENT):
            return None

        let_name = Identifier(
            token=self._current_token,
            value=self._current_token.literal
        )

        if not self._expected_token(TokenType.ASSIGN):
            return None

        # TODO: Parse expression
        let_value = None
        while self._current_token.token_type != TokenType.SEMICOLON:
            self._advance_token()

        return LetStatement(
            token=let_token,
            name=let_name,
            value=let_value
        )
