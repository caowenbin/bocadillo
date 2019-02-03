import inspect
from typing import Any, Callable, Dict, Iterable, List, Type, Set


class QueryParamsConverter:
    def __init__(self, func, route_parameters: Set[str]):
        sig = inspect.signature(func)

        self._query_parameters: Dict[str, bool] = {}
        for parameter in sig.parameters.values():
            if parameter.name in {*route_parameters, "req", "res"}:
                continue
            required = parameter.default is inspect.Parameter.empty
            self._query_parameters[parameter.name] = required

        self._converter = build_converter(func, fields=self._query_parameters)

    def all(self) -> Iterable[str]:
        return self._query_parameters.keys()

    def required(self) -> Set[str]:
        return {
            param
            for param, required in self._query_parameters.items()
            if required
        }

    def __call__(self, *args, **kwargs):
        return self._converter(*args, **kwargs)


class ConversionError(Exception):
    """Raised when conversion has failed."""

    def __init__(self, errors: List[str]):
        super().__init__(errors)
        self.errors = errors


class ConverterMustBeCallable(ValueError):
    """Raised when attempting to use a non-callable as a converter."""


FieldConverter = Callable[[str], Any]
Converter = Callable[[Dict[str, str]], Dict[str, Any]]


def build_converter(func: Callable, fields: Iterable[str]) -> Converter:
    parameters = inspect.signature(func).parameters

    field_converters: Dict[str, FieldConverter] = {}

    for field in fields:
        parameter = parameters[field]
        converter = _get_field_converter(
            (
                parameter.annotation
                if parameter.annotation is not inspect.Parameter.empty
                else lambda value: value
            )
        )
        if not callable(converter):
            raise ConverterMustBeCallable(converter)

        field_converters[field] = converter

    def convert(data: Dict[str, str]) -> Dict[str, Any]:
        errors = []
        converted = {}

        for key, value in data.items():
            try:
                converted[key] = field_converters[key](value)
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


_SPECIAL_FIELD_CONVERTERS: Dict[Type, FieldConverter] = {bool: _bool}


def _get_field_converter(base: Type) -> Converter:
    return _SPECIAL_FIELD_CONVERTERS.get(base, base)
