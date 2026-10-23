import dataclasses

@dataclasses.dataclass(frozen=True)
class TransactionSequenceConfig:
    txn_pct: int = 100
    max_num_txn: int = 10

    def __post_init__(self):
        if not (0 <= self.txn_pct <= 100):
            raise ValueError("txn_pct must be between 0 and 100")
        if not (self.max_num_txn > 0):
            raise ValueError("max_num_txn must be positive")
