from abc import (
    ABC,
    abstractmethod,
)
from enum import (
    Enum,
    auto,
    unique
)
from lpp.ast import (
    Block,
    Identifier,
)

@unique
class ObjectType(Enum):
    BOOLEAN = auto()
    INTEGER = auto()
    FUNCTION = auto()
    NULL = auto()
    RETURN = auto()
    ERROR = auto()

class Object(ABC):
    @abstractmethod
    def type(self) -> ObjectType:
        pass

    @abstractmethod
    def inspect(self) -> str:
        pass

class Enviroment(dict):
    def __init__(self):
        self._store = dict()

    def __getitem__(self, key):
        return self._store[key]
    
    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

class Integer(Object):
    def __init__(self, value: int):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.INTEGER

    def inspect(self) -> str:
        return str(self.value)

class Boolean(Object):
    def __init__(self, value: bool):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.BOOLEAN

    def inspect(self) -> str:
        return 'verdadero' if self.value else 'falso'

class Null(Object):
    def type(self) -> ObjectType:
        return ObjectType.NULL

    def inspect(self) -> str:
        return 'nulo'

class Return(Object):
    def __init__(self, value: Object):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.RETURN

    def inspect(self) -> str:
        return self.value.inspect()

class Error(Object):
    def __init__(self, message: str):
        self.message = message

    def type(self) -> ObjectType:
        return ObjectType.ERROR

    def inspect(self) -> str:
        return f'Error: {self.message}'

class Function(Object):
    def __init__(
        self,
        parameters: list[Identifier],
        body: Block,
        env: Enviroment
    ):
        self.parameters = parameters
        self.body = body
        self.env = env
    
    def type(self) -> ObjectType:
        return ObjectType.FUNCTION

    def inspect(self) -> str:
        params = ', '.join([str(p) for p in self.parameters])
        return f'procedimiento({params}) {{\n{str(self.body)}\n}}'
