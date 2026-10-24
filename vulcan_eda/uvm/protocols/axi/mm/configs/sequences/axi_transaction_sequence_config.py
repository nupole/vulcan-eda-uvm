import dataclasses

@dataclasses.dataclass(frozen=True)
class AxiTransactionSequenceConfig:
    num_txn: int = 10
    write_pct: int = 50
    min_address: int = 0
    max_address: int | None = None

    def __post_init__(self):
        if not (self.num_txn > 0):
            raise ValueError("num_txn must be positive")
        if not (0 <= self.write_pct <= 100):
            raise ValueError("write_pct must be between 0 and 100")
        if not (self.min_address >= 0):
            raise ValueError("min_address must not be negative")
        if self.max_address is not None and not (self.min_address <= self.max_address):
            raise ValueError("min_address must not be greater than max_address")
