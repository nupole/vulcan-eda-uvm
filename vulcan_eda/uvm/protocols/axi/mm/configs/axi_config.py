import dataclasses
import enum

@dataclasses.dataclass(frozen=True)
class AxiConfig:
    class Profile(enum.Enum):
        LITE = enum.auto()

    profile: Profile
    bytes_per_beat: int
    address_width: int

    @classmethod
    def from_pins(cls, profile, wdata, awaddr):
        if not (len(wdata) % 8 == 0):
            raise ValueError("wdata width must be a multiple of 8")
        return cls(profile=profile, bytes_per_beat=len(wdata) // 8, address_width=len(awaddr))

    def __post_init__(self):
        if not (self.bytes_per_beat > 0 and self.bytes_per_beat & (self.bytes_per_beat - 1) == 0):
            raise ValueError("bytes_per_beat must be a power of two")
        if self.profile is AxiConfig.Profile.LITE and not (self.bytes_per_beat in (4, 8)):
            raise ValueError("AXI4-Lite data must be 32 or 64 bits wide")
        if not (self.address_width > 0):
            raise ValueError("address_width must be positive")
