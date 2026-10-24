import dataclasses

@dataclasses.dataclass(frozen=True)
class GeneratorConfig:
    def __post_init__(self):
        for field in dataclasses.fields(self):
            if field.name.endswith("_generator"):
                generator = getattr(self, field.name)
                if iter(generator) is generator:
                    raise TypeError(f"{field.name} must be re-iterable, not a one-shot iterator; use a generator such as IterableGenerator")
                try:
                    hash(generator)
                except TypeError:
                    raise TypeError(f"{field.name} must be immutable; use a tuple or a generator instead of a list") from None
