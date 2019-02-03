import inspect
from typing import Any, Callable, Dict, List, Type


class ConversionError(Exception):
    """Raised when conversion has failed."""

    def __init__(self, errors: List[str]):
        super().__init__(errors)
        self.errors = errors


Converter = Callable[[str], Any]
Validator = Callable[[Dict[str, str]], Dict[str, Any]]


def identity(value):
    return value


def validator(func: Callable) -> Validator:
    sig = inspect.signature(func)

    converters: Dict[str, Converter] = {
        name: _get_converter(
            (
                parameter.annotation
                if parameter.annotation is not inspect.Parameter.empty
                else identity
            )
        )
        for name, parameter in sig.parameters.items()
    }

    def convert(data: Dict[str, str]) -> Dict[str, Any]:
        errors = []
        converted = {}
        for key, value in data.items():
            try:
                converted[key] = converters[key](value)
            except KeyError:
                # `func` had no argument called `key`. Ignore.
                pass
            except ValueError as exc:
                errors.append(str(exc))
        if errors:
            raise ConversionError(errors)
        return converted

    return convert


# Special converters


def _bool(value: str) -> bool:
    # TODO
    return bool(value)


_SPECIAL_CONVERTERS: Dict[Type, Converter] = {bool: _bool}


def _get_converter(base: Type) -> Converter:
    return _SPECIAL_CONVERTERS.get(base, base)
