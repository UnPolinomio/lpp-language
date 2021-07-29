from lpp.ast import Program
from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.token import (
    Token,
    TokenType,
)

EOF_TOKEN = Token(TokenType.EOF, '')

def _print_parse_errors(errors: list[str]) -> None:
    for error in errors:
        print('--- Error ---')
        print(error)

def start_repl() -> None:
    while (source := input('>> ')) != 'salir()':
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()

        if len(parser.errors) > 0:
            _print_parse_errors(parser.errors)
            continue

        print(program)
