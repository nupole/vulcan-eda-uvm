import dataclasses

from vulcan_eda.uvm.configs.base_config import BaseConfig
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence
from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

@dataclasses.dataclass(frozen=True, kw_only=True)
class TranslationLayerConfig(BaseConfig):
    translation_sequence_type: type[TranslationSequence] | None = None
    translation_subscriber_type: type[TranslationSubscriber] | None = None
    forwarded_configs: tuple[BaseConfig, ...] = ()

    def __post_init__(self):
        if self.translation_sequence_type is None and self.translation_subscriber_type is None:
            raise ValueError("translation_sequence_type or translation_subscriber_type must be set")
        if self.translation_sequence_type is not None and not issubclass(self.translation_sequence_type, TranslationSequence):
            raise TypeError("translation_sequence_type must be a TranslationSequence")
        if self.translation_subscriber_type is not None and not issubclass(self.translation_subscriber_type, TranslationSubscriber):
            raise TypeError("translation_subscriber_type must be a TranslationSubscriber")
        if self.translation_sequence_type is not None and self.translation_sequence_type.uses_responses and self.translation_subscriber_type is None:
            raise ValueError("translation_sequence_type uses responses, so translation_subscriber_type must be set")
        object.__setattr__(self, "forwarded_configs", tuple(self.forwarded_configs))
        if not all(isinstance(forwarded_config, BaseConfig) for forwarded_config in self.forwarded_configs):
            raise TypeError("forwarded_configs must contain only BaseConfig instances")
