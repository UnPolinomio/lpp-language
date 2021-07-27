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
        name: Optional[Identifier] = None,
        value: Optional[Expression] = None
    ) -> None:

        super().__init__(token)
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f'{self.token_literal()} {str(self.name)} = {str(self.value)}'
    