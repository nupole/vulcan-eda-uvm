import pytest
import pyuvm

from vulcan_eda.uvm.configs.tests import VerdictConfig

def test_has_no_default_owner():
    with pytest.raises(pyuvm.UVMConfigItemNotFound, match="no VerdictConfig set for env.scoreboard"):
        VerdictConfig.get(pyuvm.uvm_component("scoreboard", pyuvm.uvm_component("env", None)))

def test_reaches_every_component_below_its_owner():
    owner = pyuvm.uvm_component("owner", None)
    VerdictConfig(owner).set(owner, "*")
    assert VerdictConfig.get(pyuvm.uvm_component("scoreboard", pyuvm.uvm_component("env", owner))).owner is owner
