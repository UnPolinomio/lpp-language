from typing import cast
from lpp.object import (
    Builtin,
    Error,
    Integer,
    Object,
    String,
)

_WRONG_NUMBER_OF_ARGS = 'número incorrecto de argumentos para longitud, se recibieron {}, se requieren {}'
_UNSUPPORTED_ARGUMENT_TYPE = 'argumento para longitud sin soporte, se recibió {}'

def longitud(*args: Object) -> Object:
    if len(args) != 1:
        return Error(_WRONG_NUMBER_OF_ARGS.format(len(args), 1))

    if type(args[0]) == String:
        argument = cast(String, args[0])
        return Integer(len(argument.value))
    
    return Error(_UNSUPPORTED_ARGUMENT_TYPE.format(args[0].type().name))

BUILTINS: dict[str, Builtin] = {
    'longitud': Builtin(fn=longitud),
}
