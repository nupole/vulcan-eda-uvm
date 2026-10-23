import dataclasses

from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

@dataclasses.dataclass(frozen=True)
class TranslationLayerConfig:
    translation_sequence_type: type[TranslationSequence]
    forwarded_configs: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if not issubclass(self.translation_sequence_type, TranslationSequence):
            raise TypeError("translation_sequence_type must be a TranslationSequence")
