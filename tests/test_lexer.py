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
        source = '=+-/*<>!'
        lexer = Lexer(source)

        tokens: list[Token] = []
        for _ in range(len(source)):
            tokens.append(lexer.next_token())

        expected_tokens = [
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.PLUS, '+'),
            Token(TokenType.MINUS, '-'),
            Token(TokenType.DIVISION, '/'),
            Token(TokenType.MULTIPLICATION, '*'),
            Token(TokenType.LT, '<'),
            Token(TokenType.GT, '>'),
            Token(TokenType.NEGATION, '!'),

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

    def test_assignment(self) -> None:
        source = "variable cinco = 5;"
        lexer = Lexer(source)

        tokens: list[Token] = []
        for _ in range(5):
            tokens.append(lexer.next_token())

        expected_tokens = [
            Token(TokenType.LET, 'variable'),
            Token(TokenType.IDENT, 'cinco'),
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.INT, '5'),
            Token(TokenType.SEMICOLON, ';'),
        ]

        self.assertEqual(tokens, expected_tokens)

    def test_function_declaration(self) -> None:
        source = '''
            variable suma = procedimiento(x, y) {
                x + y;
            };
        '''
        lexer = Lexer(source)
        tokens: list[Token] = []

        for _ in range(16):
            tokens.append(lexer.next_token())

        expected_tokens = [
            Token(TokenType.LET, 'variable'),
            Token(TokenType.IDENT, 'suma'),
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.FUNCTION, 'procedimiento'),
            Token(TokenType.LPAREN, '('),
            Token(TokenType.IDENT, 'x'),
            Token(TokenType.COMMA, ','),
            Token(TokenType.IDENT, 'y'),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.IDENT, 'x'),
            Token(TokenType.PLUS, '+'),
            Token(TokenType.IDENT, 'y'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.RBRACE, '}'),
            Token(TokenType.SEMICOLON, ';'),
        ]
        self.assertEqual(tokens, expected_tokens)

    def test_function_call(self) -> None:
        source: str = 'variable resultado = suma(dos, tres);'
        lexer: Lexer = Lexer(source)

        tokens: list[Token] = []
        for i in range(10):
            tokens.append(lexer.next_token())

        expected_tokens: list[Token] = [
            Token(TokenType.LET, 'variable'),
            Token(TokenType.IDENT, 'resultado'),
            Token(TokenType.ASSIGN, '='),
            Token(TokenType.IDENT, 'suma'),
            Token(TokenType.LPAREN, '('),
            Token(TokenType.IDENT, 'dos'),
            Token(TokenType.COMMA, ','),
            Token(TokenType.IDENT, 'tres'),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.SEMICOLON, ';'),
        ]

        self.assertEquals(tokens, expected_tokens)

    def test_control_statement(self) -> None:
        source = '''
            si(5 < 10) {
                regresa verdadero;
            } si_no {
                regresa falso;
            }
        '''
        lexer = Lexer(source)
        tokens: list[Token] = []

        for _ in range(17):
            tokens.append(lexer.next_token())
        
        expected_tokens: list[Token] = [
            Token(TokenType.IF, 'si'),
            Token(TokenType.LPAREN, '('),
            Token(TokenType.INT, '5'),
            Token(TokenType.LT, '<'),
            Token(TokenType.INT, '10'),
            Token(TokenType.RPAREN, ')'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.RETURN, 'regresa'),
            Token(TokenType.TRUE, 'verdadero'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.RBRACE, '}'),
            Token(TokenType.ELSE, 'si_no'),
            Token(TokenType.LBRACE, '{'),
            Token(TokenType.RETURN, 'regresa'),
            Token(TokenType.FALSE, 'falso'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.RBRACE, '}'),
        ]
        self.assertEqual(tokens, expected_tokens)

    def test_two_character_operator(self) -> None:
        source = '''
            10 == 10;
            10 != 9;
        '''

        lexer = Lexer(source)
        tokens: list[Token] = []

        for _ in range(8):
            tokens.append(lexer.next_token())

        expected_tokens: list[Token] = [
            Token(TokenType.INT, '10'),
            Token(TokenType.EQ, '=='),
            Token(TokenType.INT, '10'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.INT, '10'),
            Token(TokenType.NOT_EQ, '!='),
            Token(TokenType.INT, '9'),
            Token(TokenType.SEMICOLON, ';'),
        ]
        self.assertEqual(tokens, expected_tokens)

    def test_string(self) -> None:
        source = '''
            "foo";
            "foo bar";
        '''
        lexer = Lexer(source)
        tokens: list[Token] = []
        for _ in range(4):
            tokens.append(lexer.next_token())
        
        expected_tokens: list[Token] = [
            Token(TokenType.STRING, 'foo'),
            Token(TokenType.SEMICOLON, ';'),
            Token(TokenType.STRING, 'foo bar'),
            Token(TokenType.SEMICOLON, ';'),
        ]
        self.assertEqual(tokens, expected_tokens)
