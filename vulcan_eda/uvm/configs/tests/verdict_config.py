import dataclasses

import pyuvm

from vulcan_eda.uvm.configs.base_config import BaseConfig

@dataclasses.dataclass(frozen=True)
class VerdictConfig(BaseConfig):
    owner: pyuvm.uvm_component
