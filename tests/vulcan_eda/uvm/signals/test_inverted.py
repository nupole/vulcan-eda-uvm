import pathlib

import cocotb
import cocotb.clock
import cocotb.types
import cocotb_tools.runner

import pytest
import pyuvm

import vulcan_eda.uvm

from vulcan_eda.uvm.signals import BaseSignal, Bundle, Constant, Inverted, Signal

from tests.support.components import create_agent
from tests.support.signals import Handle

def test_is_a_base_signal():
    assert isinstance(Inverted(Handle(1)), BaseSignal)

def test_reads_the_inverse_of_a_single_bit():
    assert Inverted(Handle(1, value=0)).value == 1

def test_drives_the_inverse_of_a_single_bit():
    handle = Handle(1, value=0)
    Inverted(handle).value = 0
    assert handle.value == 1

def test_inverts_integers_within_the_width():
    handle = Handle(4, value=0b0101)
    inverted = Inverted(handle)
    assert inverted.value == 0b1010
    inverted.value = 0b0011
    assert handle.value == 0b1100

def test_inverts_sampled_values_and_keeps_unknowns():
    inverted = Inverted(Handle(4, value=cocotb.types.LogicArray("10X0")))
    assert inverted.value == cocotb.types.LogicArray("01X1")

def test_len_is_the_wrapped_width():
    assert len(Inverted(Handle(12))) == 12

def test_random_value_is_drivable_and_fits_the_width():
    handle = Handle(8)
    inverted = Inverted(handle)
    values = {inverted.random_value() for _ in range(200)}
    assert all(0 <= value < 2 ** 8 for value in values) and len(values) > 1
    inverted.value = inverted.random_value()

def test_double_inversion_is_the_original():
    handle = Handle(4, value=0b0110)
    assert Inverted(Inverted(handle)).value == 0b0110

def test_wraps_signals_it_is_given():
    signal = Signal(Handle(1, value=1))
    assert Inverted(signal).value == 0

def test_rejects_signals_without_a_width():
    with pytest.raises(TypeError):
        Inverted(Constant(1))

class InvertedEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        self.stimulus_agent = create_agent(self, "stimulus_agent", vulcan_eda.uvm.interfaces.SynchronousDataInterface(dut.clk, Bundle(dut.ref_bit_in, Inverted(dut.bit_n_in), dut.ref_bus_in, Inverted(dut.bus_n_in))))
        self.reference_agent = create_agent(self, "reference_agent", vulcan_eda.uvm.interfaces.SynchronousDataInterface(dut.clk, Bundle(dut.ref_bit_out, dut.ref_bus_out)), pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.write_agent = create_agent(self, "write_agent", vulcan_eda.uvm.interfaces.SynchronousDataInterface(dut.clk, Bundle(dut.bit_out, dut.bus_out)), pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.read_agent = create_agent(self, "read_agent", vulcan_eda.uvm.interfaces.SynchronousDataInterface(dut.clk, Bundle(Inverted(dut.bit_n_out), Inverted(dut.bus_n_out))), pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.write_scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("write_scoreboard", self)
        self.read_scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("read_scoreboard", self)

    def connect_phase(self):
        for scoreboard in (self.write_scoreboard, self.read_scoreboard):
            self.reference_agent.analysis_port.connect(scoreboard.expected_data_analysis_fifo.analysis_export)
        self.write_agent.analysis_port.connect(self.write_scoreboard.actual_data_analysis_fifo.analysis_export)
        self.read_agent.analysis_port.connect(self.read_scoreboard.actual_data_analysis_fifo.analysis_export)

@pyuvm.test()
class InvertedTest(vulcan_eda.uvm.tests.BaseTest):
    timeout_us = 100

    def build_phase(self):
        self.env = InvertedEnv("env", self)

    async def stimulus(self):
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        data_sequence = vulcan_eda.uvm.sequences.DataSequence.create("data_sequence")
        data_sequence.data_generator = [(bit, bit, bus, bus) for bit in range(2) for bus in range(16)]
        await data_sequence.start(self.env.stimulus_agent.sequencer)

def test_inverted(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_inverted",
        sources = [current_dir / "test_inverted.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_inverted",
        hdl_toplevel = "test_inverted",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"],
        plusargs = ["--fst=waves.fst"]
    )
