from unittest import TestCase
from lpp.token import Token, TokenType
from lpp.lexer import Lexer

class LexerTest(TestCase):
    def test_ilegal(self) -> None:
        source = '¡¿@'
        lexer = Lexer(source)

        tokens: list[Token] = []
        for _ in range(len(source)):
            tokens.append(lexer.next_token())

        expected_tokens = [
            Token(TokenType.ILLEGAL, '¡'),
            Token(TokenType.ILLEGAL, '¿'),
            Token(TokenType.ILLEGAL, '@'),
        ]

        self.assertEqual(tokens, expected_tokens)

    def test_one_character_operator(self) -> None:
        source = '=+'
        lexer = Lexer(source)

        tokens: list[Token] = []
        for _ in range(len(source)):
            tokens.append(lexer.next_token())

        expected_tokens = [
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.PLUS, '+'),
        ]

        self.assertEqual(tokens, expected_tokens)

    def test_eof(self)-> None:
        source = '+'
        lexer = Lexer(source)

        tokens: list[Token] = []
        for _ in range(len(source) + 1):
            tokens.append(lexer.next_token())

        expected_tokens = [
            Token(TokenType.PLUS, '+'),
            Token(TokenType.EOF, ''),
        ]

        self.assertEqual(tokens, expected_tokens)

    def test_delimiters(self) -> None:
        source = '(){},;'
        lexer = Lexer(source)

        tokens: list[Token] = []
        for _ in range(len(source)):
            tokens.append(lexer.next_token())

        expected_tokens = [
            Token(TokenType.LPAREN, '('),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.RBRACE, '}'),
            Token(TokenType.COMMA, ','),
            Token(TokenType.SEMICOLON, ';'),
        ]

        self.assertEqual(tokens, expected_tokens)
