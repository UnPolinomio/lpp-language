from unittest import TestCase
from typing import (
    cast,
    Any,
    Union,
)

from lpp.lexer import Lexer
from lpp.parser import Parser
from lpp.object import (
    Enviroment,
    Object,
    Integer,
    Boolean,
    Error,
    Function,
    String,
)
from lpp.evaluator import (
    NULL,
    evaluate,
)

class EvaluatorTest(TestCase):
    def test_integer_evaluation(self) -> None:
        tests: list[tuple[str, int]] = [
            ('5', 5),
            ('10', 10),
            ('-5', -5),
            ('-10', -10),
            ('5 + 5', 10),
            ('5 - 10', -5),
            ('2 * 2 * 2 * 2', 16),
            ('2 * 5 - 3', 7), 
            ('50 / 2', 25),
            ('2 * (5 - 3)', 4),
            ('(2 + 7) / 3', 3),
            (' 50 / 2 * 2 + 10', 60),
            ('5 / 2', 2),
        ]

        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)
    
    def test_boolean_expression(self) -> None:
        tests: list[tuple[str, bool]] = [
            ('verdadero', True),
            ('falso', False),
            ('1 < 2', True),
            ('1 > 2', False),
            ('1 == 2', False),
            ('1 == 1', True),
            ('1 != 2', True),
            ('1 != 1', False),
            ('verdadero == verdadero', True),
            ('falso == falso', True),
            ('verdadero != verdadero', False),
            ('falso != falso', False),
            ('(1 < 2) == verdadero', True),
            ('(1 < 2) == falso', False),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

    def test_bang_operator(self) -> None:
        tests: list[tuple[str, bool]] = [
            ('!verdadero', False),
            ('!falso', True),
            ('!!verdadero', True),
            ('!!falso', False),
            ('!5', False),
            ('!!5', True),
        ]

        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

    def test_if_else_evaluation(self) -> None:
        test: list[tuple[str, Any]] = [
            ('si (verdadero) { 10 }', 10),
            ('si (falso) { 10 }', None),
            ('si (1) { 10 }', 10),
            ('si (1 < 2) { 10 }', 10),
            ('si (1 > 2) { 10 }', None),
            ('si (1 < 2) { 10 } si_no { 20 }', 10),
            ('si (1 > 2 ) { 10 } si_no { 20 }', 20),
        ]
        for source, expected in test:
            evaluated = self._evaluate_tests(source)
            if type(expected) == int:
                self._test_integer_object(evaluated, expected)
            else:
                self._test_null_object(evaluated)

    def test_result_evaluation(self) -> None:
        test: list[tuple[str, int]] = [
            ('regresa 10;', 10),
            ('regresa 10; 9;', 10),
            ('regresa 2 * 5; 9', 10),
            ('9; regresa 3 * 6; 9;', 18),
            ('''
                si (10 > 1) {
                    si (20 > 10) {
                        regresa 1;
                    }
                    regresa 0;
                }
            '''
            , 1),
        ]
        for source, expected in test:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def test_error_handling(self) -> None:
        tests: list[tuple[str, str]] = [
            (
                '5 + verdadero',
                'Discrepancia de tipos: INTEGER + BOOLEAN',
            ),
            (
                '5 + verdadero; 9;',
                'Discrepancia de tipos: INTEGER + BOOLEAN',
            ),
            (
                '-verdadero',
                'Operador desconocido: -BOOLEAN',
            ),
            (
                'verdadero + falso',
                'Operador desconocido: BOOLEAN + BOOLEAN',
            ),
            (
                '5; verdadero - falso; 10;',
                'Operador desconocido: BOOLEAN - BOOLEAN',
            ),
            (
                '''
                    si (10 > 7) {
                        regresa verdadero + falso;
                    }
                ''',
                'Operador desconocido: BOOLEAN + BOOLEAN',
            ),
            (
                '''
                    si (5 < 2) {
                        regresa 1;
                    } si_no {
                        regresa verdadero / falso;
                    }
                ''',
                'Operador desconocido: BOOLEAN / BOOLEAN',
            ),
            (
                'foobar;',
                'Identificador no encontrado: foobar',
            ),
            ('"Foo" - "Bar";', 'Operador desconocido: STRING - STRING'),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self.assertIsInstance(evaluated, Error)
            evaluated = cast(Error, evaluated)
            self.assertEqual(evaluated.message, expected)

    def test_assignment_evaluation(self) -> None:
        tests: list[tuple[str, int]] = [
            ('variable a = 5; a;', 5),
            ('variable a = 5 * 5; a', 25),
            ('variable a = 5; variable b = a; b;', 5),
            ('variable a = 5; variable b = a; variable c = a + b + 5; c;', 15),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def test_function_evaluation(self) -> None:
        source = 'procedimiento(x) { x + 2; };'
        evaluated = self._evaluate_tests(source)

        self.assertIsInstance(evaluated, Function)
        evaluated = cast(Function, evaluated)

        self.assertEqual(len(evaluated.parameters), 1)
        self.assertEqual(str(evaluated.parameters[0]), 'x')
        self.assertEqual(str(evaluated.body), '(x + 2)')

    def test_function_calls(self) -> None:
        tests: list[tuple[str, int]] = [
            (
                'variable identidad = procedimiento(x) { x }; identidad(5);',
                5,
            ),
            (
                '''
                    variable identidad = procedimiento(x) {
                        regresa x;
                    };
                    identidad(5);
                ''',
                5,
            ),
            (
                '''
                    variable doble = procedimiento(x) {
                        regresa x * 2;
                    };
                    doble(5);
                ''',
                10,
            ),
            (
                '''
                    variable suma = procedimiento(x, y) {
                        regresa x + y;
                    };
                    suma(3, 8);
                ''',
                11,
            ),
            (
                '''
                    variable suma = procedimiento(x, y) {
                        regresa x + y;
                    };
                    suma(5 + 5, suma(10, 10));
                ''',
                30,
            ),
            ('procedimiento(x) { x }(5);', 5),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_integer_object(evaluated, expected)

    def test_string_evaluation(self) -> None:
        tests: list[tuple[str, str]] = [
            ('"Hola";', 'Hola'),
            ('procedimiento() { regresa "Hola"; }();', 'Hola'),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self.assertIsInstance(evaluated, String)
            evaluated = cast(String, evaluated)
            self.assertEqual(evaluated.value, expected)

    def test_string_concatenation(self) -> None:
        tests: list[tuple[str, str]] = [
            ('"Foo" + "bar";', "Foobar"),
            ('"Foo" + " " + "bar";', "Foo bar"),
            (
                '''
                    variable saludo = procedimiento(nombre) {
                        regresa "Hola " + nombre + "!";
                    };
                    saludo("Pepito");
                ''',
                "Hola Pepito!",
            ),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_string_object(evaluated, expected)

    def test_string_comparison(self) -> None:
        tests: list[tuple[str, bool]] = [
            ('"a" == "a";', True),
            ('"a" != "a";', False),
            ('"a" == "b";', False),
            ('"a" != "b";', True),
        ]
        for source, expected in tests:
            evaluated = self._evaluate_tests(source)
            self._test_boolean_object(evaluated, expected)

    def test_builtin_functions(self) -> None:
        test: list[tuple[str, Union[int, str]]] = [
            ('longitud("");', 0),
            ('longitud("cuatro");', 6),
            ('longitud("Hola mundo");', 10),
            ('longitud(1);', 'argumento para longitud sin soporte, se recibió INTEGER'),
            (
                'longitud("uno", "dos")',
                'número incorrecto de argumentos para longitud, se recibieron 2, se requieren 1',
            ),
        ]
        for source, expected in test:
            evaluated = self._evaluate_tests(source)

            if type(expected) == int:
                expected = cast(int, expected)
                self._test_integer_object(evaluated, expected)
            else:
                expected = cast(str, expected)
                self._test_error_object(evaluated, expected)

    def _evaluate_tests(self, source: str) -> Object:
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        env = Enviroment()

        evaluated = evaluate(program, env)

        assert evaluated is not None
        return evaluated

    def _test_integer_object(self, evaluated: Object, expected: int) -> None:
        self.assertIsInstance(evaluated, Integer)
        evaluated = cast(Integer, evaluated)

        self.assertEqual(evaluated.value, expected)

    def _test_boolean_object(self, evaluated: Object, expected: bool) -> None:
        self.assertIsInstance(evaluated, Boolean)
        evaluated = cast(Boolean, evaluated)

        self.assertEqual(evaluated.value, expected)

    def _test_null_object(self, evaluated: Object) -> None:
        self.assertIs(evaluated, NULL)

    def _test_string_object(self, evaluated: Object, expected: str) -> None:
        self.assertIsInstance(evaluated, String)
        evaluated = cast(String, evaluated)

        self.assertEqual(evaluated.value, expected)

    def _test_error_object(self, evaluated: Object, expected: str) -> None:
        self.assertIsInstance(evaluated, Error)
        evaluated = cast(Error, evaluated)

        self.assertEqual(evaluated.message, expected)
