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
from typing import Protocol

@unique
class ObjectType(Enum):
    BOOLEAN = auto()
    INTEGER = auto()
    STRING = auto()
    FUNCTION = auto()
    NULL = auto()
    RETURN = auto()
    BUILTIN = auto()
    ERROR = auto()

class Object(ABC):
    @abstractmethod
    def type(self) -> ObjectType:
        pass

    @abstractmethod
    def inspect(self) -> str:
        pass

class Enviroment(dict):
    def __init__(self, outer=None):
        self._store = dict()
        self._outer = outer

    def __getitem__(self, key):
        try:
            return self._store[key]
        except KeyError as e:
            if self._outer is not None:
                return self._outer[key]
            raise e
    
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

class String(Object):
    def __init__(self, value: str):
        self.value = value
    
    def type(self) -> ObjectType:
        return ObjectType.STRING
    
    def inspect(self) -> str:
        return f'"{self.value}"'

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

class BuiltinFunction(Protocol):
    def __call__(self, *args: Object) -> Object: ...

class Builtin(Object):
    def __init__(self, fn: BuiltinFunction):
        self.fn = fn

    def type(self) -> ObjectType:
        return ObjectType.BUILTIN
    
    def inspect(self) -> str:
        return 'builtin function'
