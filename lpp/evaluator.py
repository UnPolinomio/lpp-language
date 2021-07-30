from typing import (
    Optional,
    cast,
)
import lpp.ast as ast
from lpp.object import (
    Integer,
    Object,
    Boolean,
)

TRUE = Boolean(True)
FALSE = Boolean(False)

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

    return None

def _evaluate_statements(statemets: list[ast.Statement]) -> Optional[Object]:
    result: Optional[Object] = None
    for statement in statemets:
        result = evaluate(statement)

    return result

def _to_boolean_object(value: bool) -> Boolean:
    return TRUE if value else FALSE
