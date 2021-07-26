from lpp.token import Token, TokenType
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

class Lexer:
    def __init__(self, source: str) -> None:
        self._source = source
        self._character: str = '' # _character is the current character
        self._read_position: int = 0 # _read_position is the index of the next character to read
        self._position: int = -1 # _position is the index of the current character

        self._read_character()

    def next_token(self) -> Token:
        for (regex, token_type) in TOKEN_REGEX:
            if regex.match(self._character):
                token = Token(token_type, self._character)
                self._read_character()
                return token

        token =  Token(TokenType.ILLEGAL, self._character)
        self._read_character()
        return token

    def _read_character(self) -> None:
        if self._read_position >= len(self._source):
            self._character = ''
        else:
            self._character = self._source[self._read_position]
            self._position = self._read_position
            self._read_position += 1
