#!/usr/bin/env python

from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.evaluator import evaluate
from lpp.object import Enviroment
from sys import argv

if __name__ == '__main__':
    with open(argv[1], 'r') as f:
        source = f.read()

    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()

    env = Enviroment()
    evaluation = evaluate(program, env)

    if evaluation:
        print(evaluation.inspect())
