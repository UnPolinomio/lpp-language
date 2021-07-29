from typing import (
    Optional,
    Callable,
)
from enum import (
    IntEnum,
    unique,
)

from lpp.ast import (
    Expression,
    Identifier,
    Program,
    Statement,
    LetStatement,
    ReturnStatement,
    ExpressionStatement,
    Integer,
    Prefix,
    Infix,
    Boolean
)
from lpp.lexer import Lexer
from lpp.token import Token, TokenType

@unique
class Precedence(IntEnum):
    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7

PRECEDENCES: dict[TokenType, Precedence] = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,

    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,

    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,

    TokenType.MULTIPLICATION: Precedence.PRODUCT,
    TokenType.DIVISION: Precedence.PRODUCT,
}

PrefixParseFn = Callable[[], Optional[Expression]]
InfixParseFn = Callable[[Expression], Optional[Expression]]
PrefixParseFns = dict[TokenType, PrefixParseFn]
InfixParseFns = dict[TokenType, InfixParseFn]

class Parser:

    def __init__(self, lexer: Lexer) -> None:
        self._lexer = lexer

        self._prefix_parse_fns: PrefixParseFns = self._register_prefix_fns()
        self._infix_parse_fns: InfixParseFns = self._register_infix_fns()

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
        if self._current_token.token_type == TokenType.RETURN:
            return self._parse_return_statement()
        else:
            return self._parse_expression_statement()

    def _parse_let_statement(self) -> Optional[LetStatement]:
        let_token = self._current_token

        if not self._expected_token(TokenType.IDENT):
            return None

        let_name = self._parse_identifier()

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

    def _parse_return_statement(self) -> Optional[ReturnStatement]:
        return_token = self._current_token

        self._advance_token()

        # TODO: Parse expression
        while self._current_token.token_type != TokenType.SEMICOLON:
            self._advance_token()

        return ReturnStatement(token=return_token)

    def _parse_expression_statement(self) -> Optional[ExpressionStatement]:
        expression_token = self._current_token
        expression_expression = self._parse_expression(Precedence.LOWEST)

        if self._peek_token.token_type == TokenType.SEMICOLON:
            self._advance_token()

        return ExpressionStatement(
            token=expression_token,
            expression=expression_expression,
        )

    def _parse_integer(self) -> Optional[Integer]:
        try:
            value = int(self._current_token.literal)
        except ValueError:
            self._errors.append(
                'No se ha podido parsear el valor ' \
                f'{self._current_token.literal} como entero'
            )
            return None
        return Integer(token=self._current_token, value=value)

    def _parse_prefix_expression(self) -> Prefix:
        token = self._current_token
        self._advance_token()
        right=self._parse_expression(Precedence.PREFIX)
        return Prefix(
            token=token,
            operator=token.literal,
            right=right
        )

    def _parse_infix_expression(self, left: Expression) -> Infix:
        token = self._current_token
        precedence = self._current_precedence()
        self._advance_token()
        return Infix(
            token=token,
            operator=token.literal,
            left=left,
            right=self._parse_expression(precedence)
        )
    
    def _current_precedence(self) -> Precedence:
        try:
            return PRECEDENCES[self._current_token.token_type]
        except KeyError:
            return Precedence.LOWEST

    def _peek_precedence(self) -> Precedence:
        try:
            return PRECEDENCES[self._peek_token.token_type]
        except KeyError:
            return Precedence.LOWEST

    def _register_infix_fns(self) -> InfixParseFns:
        return {
            TokenType.EQ: self._parse_infix_expression,
            TokenType.NOT_EQ: self._parse_infix_expression,

            TokenType.LT: self._parse_infix_expression,
            TokenType.GT: self._parse_infix_expression,

            TokenType.PLUS: self._parse_infix_expression,
            TokenType.MINUS: self._parse_infix_expression,

            TokenType.MULTIPLICATION: self._parse_infix_expression,
            TokenType.DIVISION: self._parse_infix_expression,
        }

    def _register_prefix_fns(self) -> PrefixParseFns:
        return {
            TokenType.IDENT: self._parse_identifier,
            TokenType.INT: self._parse_integer,
            TokenType.MINUS: self._parse_prefix_expression,
            TokenType.NEGATION: self._parse_prefix_expression,
            TokenType.FALSE: self._parse_boolean,
            TokenType.TRUE: self._parse_boolean,
            TokenType.LPAREN: self._parse_grouped_expression,
        }

    def _parse_expression(self, precedence: Precedence) -> Optional[Expression]:
        try:
            prefix_parse_fn = self._prefix_parse_fns[self._current_token.token_type]
        except KeyError:
            self._errors.append(
                f'No se ha encontrado una función para parsear ' \
                f'{self._current_token.literal}'
            )
            return None

        left_expression = prefix_parse_fn()

        while (
            not self._peek_token.token_type == TokenType.SEMICOLON and \
            self._peek_precedence() > precedence
        ):
            try:
                infix_parse_fn = self._infix_parse_fns[self._peek_token.token_type]  
            except KeyError:
                return left_expression

            self._advance_token()
            assert left_expression is not None
            left_expression = infix_parse_fn(left_expression)

        return left_expression
        
    def _parse_identifier(self) -> Identifier:
        return Identifier(
            token=self._current_token,
            value=self._current_token.literal
        )

    def _parse_boolean(self) -> Boolean:
        return Boolean(
            token=self._current_token,
            value=self._current_token.token_type == TokenType.TRUE
        )

    def _parse_grouped_expression(self) -> Optional[Expression]:
        self._advance_token()
        expression = self._parse_expression(Precedence.LOWEST)
        if not self._expected_token(TokenType.RPAREN):
            return None

        return expression
