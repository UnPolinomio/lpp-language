from typing import (
    Optional,
    Any,
    cast,
)
import lpp.ast as ast
from lpp.object import (
    Object,
    Enviroment,
    Integer,
    Boolean,
    String,
    Null,
    Return,
    ObjectType,
    Error,
    Function,
    Builtin,
)
from lpp.builtins import BUILTINS

TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()

# Errors constants
_TYPE_MISMATCH = 'Discrepancia de tipos: {} {} {}'
_UNKNOW_PREFIX_OPERATOR = 'Operador desconocido: {}{}'
_UNKNOW_INFIX_OPERATOR = 'Operador desconocido: {} {} {}'
_UNKNOW_IDENTIFIER = 'Identificador no encontrado: {}'
_NOT_A_FUNCTION = 'No es una funcion: {}'

def evaluate(node: ast.ASTNode, env: Enviroment) -> Optional[Object]:
    node_type = type(node)

    if node_type == ast.Program:
        node = cast(ast.Program, node)
        return _evaluate_program(node, env)

    if node_type == ast.ExpressionStatement:
        node = cast(ast.ExpressionStatement, node)
        assert node.expression is not None
        return evaluate(node.expression, env)

    if node_type == ast.Integer:
        node = cast(ast.Integer, node)
        assert node.value is not None
        return Integer(node.value)

    if node_type == ast.Boolean:
        node = cast(ast.Boolean, node)
        assert node.value is not None

        return _to_boolean_object(node.value)

    if node_type == ast.StringLiteral:
        node = cast(ast.StringLiteral, node)
        return String(node.value)

    if node_type == ast.Prefix:
        node = cast(ast.Prefix, node)

        assert node.right is not None
        right = evaluate(node.right, env)

        assert right is not None
        return _evaluate_prefix_expression(node.operator, right)

    if node_type == ast.Infix:
        node = cast(ast.Infix, node)
        assert node.left is not None
        assert node.right is not None
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        assert left is not None
        assert right is not None
        return _evaluate_infix_expression(node.operator, left, right)

    if node_type == ast.Block:
        node = cast(ast.Block, node)
        return _evaluate_block_statement(node, env)

    if node_type == ast.If:
        node = cast(ast.If, node)
        return _evaluate_if_expression(node, env)

    if node_type == ast.ReturnStatement:
        node = cast(ast.ReturnStatement, node)
        assert node.return_value is not None
        value = evaluate(node.return_value, env)
        assert value is not None
        return Return(value)

    if node_type == ast.LetStatement:
        node = cast(ast.LetStatement, node)
        assert node.value is not None
        value = evaluate(node.value, env)

        env[node.name.value] = value

    if node_type == ast.Identifier:
        node = cast(ast.Identifier, node)
        return _evaluate_identifier(node, env)

    if node_type == ast.Function:
        node = cast(ast.Function, node)
        assert node.body is not None

        return Function(
            parameters=node.parameters,
            body=node.body,
            env=env,
        )

    if node_type == ast.Call:
        node = cast(ast.Call, node)
        function = evaluate(node.function, env)
        assert function is not None
        args = _evaluate_expression(node.arguments, env)
        return _apply_function(function, args)

    return None

def _evaluate_program(program: ast.Program, env: Enviroment) -> Optional[Object]:
    result: Optional[Object] = None
    for statement in program.statements:
        result = evaluate(statement, env)
        if result is not None and type(result) == Return:
            result = cast(Return, result)
            return result.value
        elif type(result) == Error:
            return result

    return result

def _evaluate_block_statement(block: ast.Block, env: Enviroment) -> Optional[Object]:
    result: Optional[Object] = None
    for statement in block.statements:
        result = evaluate(statement, env)
        if (
            result is not None and \
            result.type() in [ObjectType.RETURN, ObjectType.ERROR]
        ):
            result = cast(Return, result)
            return result

    return result

def _to_boolean_object(value: bool) -> Boolean:
    return TRUE if value else FALSE

def _evaluate_prefix_expression(operator: str, right: Object) -> Object:
    if operator == '!':
        return _evaluate_bang_operator_expression(right)
    if operator == '-':
        return _evaluate_minus_operator_expression(right)
    else:
        return _new_error(_UNKNOW_PREFIX_OPERATOR, [operator, right.type().name])

def _evaluate_bang_operator_expression(right: Object) -> Object:
    if right is TRUE:
        return FALSE
    if right is FALSE:
        return TRUE
    if right is NULL:
        return TRUE
    return FALSE

def _evaluate_minus_operator_expression(right: Object) -> Object:
    if type(right) != Integer:
        return _new_error(
            _UNKNOW_PREFIX_OPERATOR,
            ['-', right.type().name]
        )
    right = cast(Integer, right)
    return Integer(-right.value)

def _evaluate_infix_expression(operator: str, left: Object, right: Object) -> Object:
    left_type = left.type()
    right_type = right.type()
    if left_type == ObjectType.INTEGER and right_type == ObjectType.INTEGER:
        return _evaluate_integer_infix_expression(operator, left, right)
    if left_type == ObjectType.STRING and right_type == ObjectType.STRING:
        return _evaluate_string_infix_expression(operator, left, right)
    if operator == '==':
        return _to_boolean_object(left is right)
    if operator == '!=':
        return _to_boolean_object(left is not right)
    if left.type() != right.type():
        return _new_error(
            _TYPE_MISMATCH,
            [left.type().name, operator, right.type().name]
        )
    return _new_error(
        _UNKNOW_INFIX_OPERATOR,
        [left.type().name, operator, right.type().name]
    )

def _evaluate_integer_infix_expression(operator: str, left: Object, right: Object) -> Object:
    left_value = cast(Integer, left).value
    right_value = cast(Integer, right).value

    if operator == '+':
        return Integer(left_value + right_value)
    if operator == '-':
        return Integer(left_value - right_value)
    if operator == '*':
        return Integer(left_value * right_value)
    if operator == '/':
        return Integer(left_value // right_value)

    if operator == '<':
        return _to_boolean_object(left_value < right_value)
    if operator == '>':
        return _to_boolean_object(left_value > right_value)
    if operator == '==':
        return _to_boolean_object(left_value == right_value)
    if operator == '!=':
        return _to_boolean_object(left_value != right_value)

    return _new_error(
        _UNKNOW_INFIX_OPERATOR,
        [left.type().name, operator, right.type().name]
    )

def _evaluate_string_infix_expression(operator: str, left: Object, right: Object) -> Object:
    left_value = cast(String, left).value
    right_value = cast(String, right).value
    if operator == '+':
        return String(left_value + right_value)
    if operator == '==':
        return _to_boolean_object(left_value == right_value)
    if operator == '!=':
        return _to_boolean_object(left_value != right_value)
    return _new_error(
        _UNKNOW_INFIX_OPERATOR,
        [left.type().name, operator, right.type().name]
    )

def _evaluate_if_expression(if_node: ast.If, env: Enviroment) -> Optional[Object]:
    assert if_node.condition is not None
    condition = evaluate(if_node.condition, env)
    assert condition is not None
    if _is_truthy(condition):
        assert if_node.consequence is not None
        return evaluate(if_node.consequence, env)
    elif if_node.alternative is not None:
        return evaluate(if_node.alternative, env)

    return NULL

def _is_truthy(obj: Object) -> bool:
    if obj is NULL:
        return False
    if obj is TRUE:
        return True
    if obj is FALSE:
        return False
    return True

def _new_error(message: str, args: list[Any]) -> Error:
    return Error(message.format(*args))

def _evaluate_identifier(node: ast.Identifier, env: Enviroment) -> Object:
    try:
        return env[node.value]
    except KeyError:
        return BUILTINS.get(
            node.value,
            _new_error(_UNKNOW_IDENTIFIER, [node.value])
        )

def _evaluate_expression(expressions: list[ast.Expression], env: Enviroment) -> list[Object]:
    result: list[Object] = []
    for expression in expressions:
        evaluated = evaluate(expression, env)
        assert evaluated is not None
        result.append(evaluated)
        
    return result

def _apply_function(fn: Object, args: list[Object]) -> Object:
    if type(fn) == Function:
        fn = cast(Function, fn)
        extended_environment = _extended_function_enviroment(fn, args)
        evaluated = evaluate(fn.body, extended_environment)
        assert evaluated is not None
        return _unwrap_return_value(evaluated)

    if type(fn) == Builtin:
        fn = cast(Builtin, fn)
        return fn.fn(*args)

    return _new_error(_NOT_A_FUNCTION, [fn.type().name])

def _extended_function_enviroment(fn: Function, args: list[Object]) -> Enviroment:
    env = Enviroment(outer=fn.env)
    for arg, param in zip(args, fn.parameters):
        env[param.value] = arg
    
    return env

def _unwrap_return_value(obj: Object) -> Object:
    if type(obj) == Return:
        obj = cast(Return, obj)
        return obj.value
    return obj
