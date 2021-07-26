from lpp.token import Token, TokenType, lookup_token_type
from re import compile

TOKEN_REGEX = [
    (compile(r'^=$'), TokenType.ASSIGN),
    (compile(r'^\+$'), TokenType.PLUS),
    (compile(r'^$'), TokenType.EOF),
    (compile(r'^\($'), TokenType.LPAREN),
    (compile(r'^\)$'), TokenType.RPAREN),
    (compile(r'^{$'), TokenType.LBRACE),
    (compile(r'^}$'), TokenType.RBRACE),
    (compile(r'^,$'), TokenType.COMMA),
    (compile(r'^;$'), TokenType.SEMICOLON),
]
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
        for (regex, token_type) in TOKEN_REGEX:
            if regex.match(self._character):
                token = Token(token_type, self._character)
                self._read_character()
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

    def _read_character(self) -> None:
        if self._read_position >= len(self._source):
            self._character = ''
        else:
            self._character = self._source[self._read_position]
            self._position = self._read_position
            self._read_position += 1

    def _read_identifier(self) -> str:
        initial_position = self._position

        while self._is_letter(self._character):
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
