import dataclasses

import pyuvm

from vulcan_eda.uvm.configs.base_config import BaseConfig
from vulcan_eda.uvm.interfaces.base_interface import BaseInterface

@dataclasses.dataclass(frozen=True)
class AgentConfig(BaseConfig):
    interface: BaseInterface
    is_active: pyuvm.uvm_active_passive_enum = pyuvm.uvm_active_passive_enum.UVM_ACTIVE
