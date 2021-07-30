from lpp.ast import Program
from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.token import (
    Token,
    TokenType,
)
from lpp.evaluator import evaluate
from lpp.object import Enviroment

EOF_TOKEN = Token(TokenType.EOF, '')

def _print_parse_errors(errors: list[str]) -> None:
    for error in errors:
        print('--- Error ---')
        print(error)

def start_repl() -> None:
    scanned: list[str] = []
    while (source := input('>> ')) != 'salir()':
        scanned.append(source)
        lexer = Lexer(' '.join(scanned))
        parser = Parser(lexer)
        program = parser.parse_program()
        env = Enviroment()

        if len(parser.errors) > 0:
            _print_parse_errors(parser.errors)
            continue

        evaluated = evaluate(program, env)
        if evaluated is not None:
            print(evaluated.inspect())
