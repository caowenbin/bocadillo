import inspect
from typing import Any, Callable, Dict, List, Type, Set, Optional


class ConversionError(Exception):
    """Raised when conversion has failed."""

    def __init__(self, errors: List[str]):
        super().__init__(errors)
        self.errors = errors


class ConverterMustBeCallable(ValueError):
    """Raised when attempting to use a non-callable as a converter."""


FieldConverter = Callable[[str], Any]


class Converter(Callable[[Dict[str, str]], Dict[str, Any]]):
    def __init__(
        self,
        func,
        only: Optional[Set[str]] = None,
        exclude: Set[str] = None,
        field_type: str = "field",
    ):
        if exclude is None:
            exclude = set()

        self.func = func
        self.signature = inspect.signature(func)
        self.field_type = field_type

        if only is None:
            fields = {}
            for parameter in self.signature.parameters.values():
                if parameter.name in exclude:
                    continue
                required = parameter.default is inspect.Parameter.empty
                fields[parameter.name] = required
        else:
            # All specified fields are considered to be required.
            fields = {field: True for field in only}

        self._fields = fields
        self._field_converters: Dict[str, FieldConverter] = {}

        for field in self._fields:
            parameter = self.signature.parameters[field]
            converter = _get_field_converter(
                (
                    parameter.annotation
                    if parameter.annotation is not inspect.Parameter.empty
                    else lambda value: value
                )
            )
            if not callable(converter):
                raise ConverterMustBeCallable(converter)

            self._field_converters[field] = converter

    def __call__(self, data: Dict[str, str]) -> Dict[str, Any]:
        converted = {}

        errors = []
        for field, required in self._fields.items():
            if required and field not in data:
                errors.append(f"{field}: this {self.field_type} is required.")

        for key, value in data.items():
            try:
                converter = self._field_converters[key]
            except KeyError:
                # `func` had no argument called `key`. Ignore.
                pass
            else:
                try:
                    converted[key] = converter(value)
                except ValueError as exc:
                    errors.append(str(exc))

        if errors:
            raise ConversionError(errors)

        return converted


# Special field converters


def _bool(value: str) -> bool:
    # TODO
    return bool(value)


_SPECIAL_FIELD_CONVERTERS: Dict[Type, FieldConverter] = {bool: _bool}


def _get_field_converter(base: Type) -> Converter:
    return _SPECIAL_FIELD_CONVERTERS.get(base, base)
