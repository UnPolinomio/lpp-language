from typing import (
    Optional,
    cast,
)
import lpp.ast as ast
from lpp.object import (
    Integer,
    Object,
    Boolean,
    Null,
)

TRUE = Boolean(True)
FALSE = Boolean(False)
NULL = Null()

def evaluate(node: ast.ASTNode) -> Optional[Object]:
    node_type = type(node)

    if node_type == ast.Program:
        node = cast(ast.Program, node)
        return _evaluate_statements(node.statements)

    if node_type == ast.ExpressionStatement:
        node = cast(ast.ExpressionStatement, node)
        assert node.expression is not None
        return evaluate(node.expression)

    if node_type == ast.Integer:
        node = cast(ast.Integer, node)
        assert node.value is not None
        return Integer(node.value)

    if node_type == ast.Boolean:
        node = cast(ast.Boolean, node)
        assert node.value is not None

        return _to_boolean_object(node.value)

    if node_type == ast.Prefix:
        node = cast(ast.Prefix, node)

        assert node.right is not None
        right = evaluate(node.right)

        assert right is not None
        return _evaluate_prefix_expression(node.operator, right)

    return None

def _evaluate_statements(statemets: list[ast.Statement]) -> Optional[Object]:
    result: Optional[Object] = None
    for statement in statemets:
        result = evaluate(statement)

    return result

def _to_boolean_object(value: bool) -> Boolean:
    return TRUE if value else FALSE

def _evaluate_prefix_expression(operator: str, right: Object) -> Object:
    if operator == '!':
        return _evaluate_bang_operator_expression(right)
    if operator == '-':
        return _evaluate_minus_operator_expression(right)
    else:
        return NULL

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
        return NULL
    right = cast(Integer, right)
    return Integer(-right.value)
