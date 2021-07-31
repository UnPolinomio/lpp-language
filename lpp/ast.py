from abc import ABC, abstractmethod
from lpp.token import Token
from typing import Optional

class ASTNode(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class Statement(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token

    def token_literal(self) -> str:
        return self.token.literal

class Expression(ASTNode):
    def __init__(self, token: Token) -> None:
        self.token = token
    
    def token_literal(self) -> str:
        return self.token.literal

class Program(ASTNode):
    def __init__(self, statements: list[Statement]) -> None:
        self.statements = statements

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ''

    def __str__(self) -> str:
        return ''.join([str(s) for s in self.statements])

class Identifier(Expression):
    def __init__(self, token: Token, value: str) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return self.value

class LetStatement(Statement):
    def __init__(
        self,
        token: Token,
        name: Identifier,
        value: Optional[Expression] = None
    ) -> None:

        super().__init__(token)
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f'{self.token_literal()} {str(self.name)} = {str(self.value)};'

class ReturnStatement(Statement):
    def __init__(
            self,
            token: Token,
            return_value: Optional[Expression] = None
        ) -> None:
            super().__init__(token)
            self.return_value = return_value

    def __str__(self) -> str:
        return f'{self.token_literal()} {str(self.return_value)};'

class ExpressionStatement(Statement):
    def __init__(self, token: Token, expression: Optional[Expression] = None) -> None:
        super().__init__(token)
        self.expression = expression

    def __str__(self) -> str:
        return str(self.expression)

class Integer(Expression):
    def __init__(self, token: Token, value: Optional[int] = None) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)
        
class StringLiteral(Expression):
    def __init__(self, token: Token, value: str) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return self.value

class Prefix(Expression):
    def __init__(
        self,
        token: Token,
        operator: str,
        right: Optional[Expression] = None
    ) -> None:
        super().__init__(token)
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f'({self.operator}{str(self.right)})'

class Infix(Expression):
    def __init__(
        self,
        token: Token,
        left: Expression,
        operator: str,
        right: Optional[Expression] = None
    ) -> None:
        super().__init__(token)

        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        return f'({str(self.left)} {self.operator} {str(self.right)})'

class Boolean(Expression):
    def __init__(self, token: Token, value: Optional[bool] = None) -> None:
        super().__init__(token)
        self.value = value

    def __str__(self) -> str:
        return self.token_literal()

class Block(Statement):
    def __init__(self, token: Token, statements: list[Statement]) -> None:
        super().__init__(token)
        self.statements = statements

    def __str__(self) -> str:
        return ''.join([str(s) for s in self.statements])

class If(Expression):
    def __init__(
        self,
        token: Token,
        condition: Optional[Expression] = None,
        consequence: Optional[Block] = None,
        alternative: Optional[Block] = None
    ) -> None:
        super().__init__(token)
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def __str__(self) -> str:
        out = f'si {str(self.condition)} {str(self.consequence)}'
        if self.alternative:
            out += f'si_no {str(self.alternative)}'

        return out

class Function(Expression):
    def __init__(
        self,
        token: Token,
        parameters: list[Identifier] = [],
        body: Optional[Block] = None
    ) -> None:
        super().__init__(token)
        self.parameters = parameters
        self.body = body

    def __str__(self) -> str:
        params = ',  '.join([str(p) for p in self.parameters])
        return f'{self.token_literal()}({params}) {str(self.body)}'


class Call(Expression):
    def __init__(
        self,
        token: Token,
        function: Expression,
        arguments: list[Expression]
    ) -> None:
        super().__init__(token)
        self.function = function
        self.arguments = arguments

    def __str__(self) -> str:
        args = ', '.join([str(a) for a in self.arguments])
        return f'{str(self.function)}({args})'
