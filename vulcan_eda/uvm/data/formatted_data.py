import dataclasses
import enum

class FormattedData:
    def __str__(self):
        fields = ", ".join(
            f"{field.name}={FormattedData._format(getattr(self, field.name), field.metadata.get('format', ''))}"
            for field in dataclasses.fields(self) if field.repr
        )
        return f"{type(self).__qualname__}({fields})"

    @staticmethod
    def _format(value, format_spec):
        if isinstance(value, enum.Enum):
            return value.name
        if isinstance(value, tuple):
            values = [FormattedData._format(element, format_spec) for element in value]
            return f"({values[0]},)" if len(values) == 1 else f"({', '.join(values)})"
        if value is None:
            return "None"
        if isinstance(value, bytes) and format_spec == "#x":
            return f"0x{value.hex()}"
        return format(value, format_spec)
