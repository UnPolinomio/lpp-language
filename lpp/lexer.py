from lpp.token import Token, TokenType, lookup_token_type
from re import compile, Pattern
from typing import NamedTuple

class TokenRegex(NamedTuple):
    n_characters: int
    regex: Pattern[str]
    token_type: TokenType

TOKEN_REGEX = [
    TokenRegex(2, compile(r'^==$'), TokenType.EQ),
    TokenRegex(2, compile(r'^!=$'), TokenType.NOT_EQ),

    TokenRegex(1, compile(r'^=$'), TokenType.ASSIGN),
    TokenRegex(1, compile(r'^\+$'), TokenType.PLUS),
    TokenRegex(1, compile(r'^$'), TokenType.EOF),
    TokenRegex(1, compile(r'^\($'), TokenType.LPAREN),
    TokenRegex(1, compile(r'^\)$'), TokenType.RPAREN),
    TokenRegex(1, compile(r'^{$'), TokenType.LBRACE),
    TokenRegex(1, compile(r'^}$'), TokenType.RBRACE),
    TokenRegex(1, compile(r'^,$'), TokenType.COMMA),
    TokenRegex(1, compile(r'^;$'), TokenType.SEMICOLON),
    TokenRegex(1, compile(r'^<$'), TokenType.LT),
    TokenRegex(1, compile(r'^>$'), TokenType.GT),
    TokenRegex(1, compile(r'^-$'), TokenType.MINUS),
    TokenRegex(1, compile(r'^/$'), TokenType.DIVISION),
    TokenRegex(1, compile(r'^\*$'), TokenType.MULTIPLICATION),
    TokenRegex(1, compile(r'^!$'), TokenType.NEGATION),
]
TOKEN_REGEX.sort(key=lambda x: x.n_characters, reverse=True)

LETTER_REGEX = compile(r'^[a-záéíóúA-ZÁÉÍÓÚñÑ_]$')
NUMBER_REGEX = compile(r'^[0-9]$')
WHITESPACE_REGEX = compile(r'^\s+$')

class Lexer:
    def __init__(self, source: str) -> None:
        self._source = source
        self._character: str = '' # _character is the current character
        self._read_position: int = 0 # _read_position is the index of the next character to read
        self._position: int = -1 # _position is the index of the current character

        self._read_character()

    def next_token(self) -> Token:
        self._skip_whitespace()
        for (n_characters, regex, token_type) in TOKEN_REGEX:
            literal = self._character + self._peek_character(n_characters - 1)
            if regex.match(literal):
                token = Token(token_type, literal)
                self._read_character(n_characters=n_characters)
                return token

        if self._is_letter(self._character):
            literal = self._read_identifier()
            token_type = lookup_token_type(literal)

            return Token(token_type, literal)

        if self._is_number(self._character):
            literal = self._read_number()
            return Token(TokenType.INT, literal)

        token =  Token(TokenType.ILLEGAL, self._character)
        self._read_character()
        return token

    def _is_letter(self, character: str) -> bool:
        return bool(LETTER_REGEX.match(character))

    def _is_number(self, character: str) -> bool:
        return bool(NUMBER_REGEX.match(character))

    def _read_character(self, n_characters: int = 1) -> None:
        new_position = self._position + n_characters

        if new_position >= len(self._source):
            self._character = ''
            self._read_position = len(self._source) + 1
            self._position = len(self._source)
        else:
            self._character = self._source[new_position]
            self._read_position += n_characters
            self._position = self._read_position - 1

    def _read_identifier(self) -> str:
        initial_position = self._position

        if not self._is_letter(self._character):
            return ''
        
        self._read_character()
        while self._is_letter(self._character) or self._is_number(self._character):
            self._read_character()

        return self._source[initial_position:self._position]

    def _read_number(self) -> str:
        initial_position = self._position

        while self._is_number(self._character):
            self._read_character()

        return self._source[initial_position:self._position]

    def _skip_whitespace(self) -> None:
        while WHITESPACE_REGEX.match(self._character):
            self._read_character()

    def _peek_character(self, n_characters: int) -> str:
        if self._read_position + n_characters >= len(self._source):
            return self._source[self._read_position:]
        else:
            return self._source[self._read_position:self._read_position + n_characters]
