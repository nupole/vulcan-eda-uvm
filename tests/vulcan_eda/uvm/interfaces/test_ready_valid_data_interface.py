import asyncio
import pathlib
import random
import types

import cocotb
import cocotb.clock
import cocotb.triggers
import cocotb_tools.runner

import pytest
import pyuvm

import vulcan_eda.uvm

class Pair:
    def __init__(self, first, second):
        self.first = first
        self.second = second

    @classmethod
    def signals(cls, first, second):
        return vulcan_eda.uvm.signals.Bundle(first, second)

    def to_values(self):
        return (self.first, self.second)

    @classmethod
    def from_values(cls, values):
        return cls(*values)

def signal(value):
    return types.SimpleNamespace(value=value)

def test_data_type_builds_data_from_named_pins():
    receiver_interface = vulcan_eda.uvm.interfaces.ReadyValidDataReceiverInterface(None, signal(1), signal(1), {"second": signal(2), "first": signal(1)}, Pair)
    assert receiver_interface.read_ready_valid_data() == (1, 1, (1, 2))

def test_data_type_rejects_unknown_pins():
    with pytest.raises(TypeError):
        vulcan_eda.uvm.interfaces.ReadyValidDataReceiverInterface(None, signal(1), signal(1), {"first": signal(1), "third": signal(3)}, Pair)

def test_data_type_converts_values():
    transmitter_interface = vulcan_eda.uvm.interfaces.ReadyValidDataTransmitterInterface(None, signal(1), signal(1), {"first": signal(1), "second": signal(2)}, Pair)
    assert transmitter_interface._to_values(Pair(1, 2)) == (1, 2)
    assert vars(transmitter_interface._from_values((1, 2))) == vars(Pair(1, 2))

def test_no_data_type_passes_values_through():
    transmitter_interface = vulcan_eda.uvm.interfaces.ReadyValidDataTransmitterInterface(None, signal(1), signal(1), signal(2))
    assert transmitter_interface._to_values(2) == 2
    assert transmitter_interface._from_values(2) == 2

class EdgeRecorder:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.write_edges = 0

    async def _write_edge(self):
        self.write_edges += 1

    async def _read_edge(self):
        pass

class EdgeRecordingTransmitterInterface(EdgeRecorder, vulcan_eda.uvm.interfaces.ReadyValidDataTransmitterInterface):
    pass

class EdgeRecordingReceiverInterface(EdgeRecorder, vulcan_eda.uvm.interfaces.ReadyValidDataReceiverInterface):
    pass

def test_transmitter_writes_on_its_own_write_edge():
    valid, data = signal(0), signal(0)
    transmitter_interface = EdgeRecordingTransmitterInterface(None, signal(1), valid, data)
    asyncio.run(transmitter_interface.put_data(5))
    assert (transmitter_interface.write_edges, valid.value, data.value) == (1, 1, 5)

def test_transmitter_idles_valid_low_with_its_idle_generator():
    valid, data = signal(1), signal(5)
    transmitter_interface = EdgeRecordingTransmitterInterface(None, signal(1), valid, data, idle_generator=vulcan_eda.uvm.generators.ConstantGenerator(9))
    asyncio.run(transmitter_interface.put_idle())
    assert (transmitter_interface.write_edges, valid.value, data.value) == (1, 0, 9)

def test_receiver_writes_on_its_own_write_edge():
    ready = signal(0)
    receiver_interface = EdgeRecordingReceiverInterface(None, ready, signal(0), signal(0))
    asyncio.run(receiver_interface.put_data(1))
    assert (receiver_interface.write_edges, ready.value) == (1, 1)

def test_receiver_holds_ready_when_idle_by_default():
    ready = signal(1)
    receiver_interface = EdgeRecordingReceiverInterface(None, ready, signal(0), signal(0))
    asyncio.run(receiver_interface.put_idle())
    assert (receiver_interface.write_edges, ready.value) == (1, 1)

def test_receiver_drives_its_idle_generator_when_idle():
    ready = signal(1)
    receiver_interface = EdgeRecordingReceiverInterface(None, ready, signal(0), signal(0), idle_generator=vulcan_eda.uvm.generators.PatternGenerator((0, 1)))
    readies = []
    for _ in range(4):
        asyncio.run(receiver_interface.put_idle())
        readies.append(ready.value)
    assert readies == [0, 1, 0, 1]

class HandshakeRecorder(pyuvm.uvm_subscriber):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.handshakes = []

    def write(self, ready_valid):
        ready, valid = ready_valid
        self.handshakes.append(ready == 1 and valid == 1)

class ReadyValidDataInterfaceEnv(pyuvm.uvm_env):
    def build_phase(self):
        dut = cocotb.top
        self.upstream_agent = self._create_agent("upstream_agent", vulcan_eda.uvm.interfaces.ReadyValidDataTransmitterInterface(dut.clk, dut.upstream_ready, dut.upstream_valid, dut.upstream_data))
        self.downstream_agent = self._create_agent("downstream_agent", vulcan_eda.uvm.interfaces.ReadyValidDataReceiverInterface(dut.clk, dut.downstream_ready, dut.downstream_valid, dut.downstream_data))
        self.handshake_agent = self._create_agent("handshake_agent", vulcan_eda.uvm.interfaces.DataInterface(dut.clk, vulcan_eda.uvm.signals.Bundle(dut.downstream_ready, dut.downstream_valid)), pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
        self.handshake_recorder = HandshakeRecorder.create("handshake_recorder", self)
        self.scoreboard = vulcan_eda.uvm.scoreboards.Scoreboard.create("scoreboard", self)

    def connect_phase(self):
        self.downstream_agent.analysis_port.connect(self.scoreboard.actual_data_analysis_fifo.analysis_export)
        self.handshake_agent.analysis_port.connect(self.handshake_recorder.analysis_export)

    def _create_agent(self, name, interface, is_active=pyuvm.uvm_active_passive_enum.UVM_ACTIVE):
        pyuvm.ConfigDB().set(self, name, "config", vulcan_eda.uvm.configs.agents.AgentConfig(interface, is_active))
        return vulcan_eda.uvm.agents.Agent.create(name, self)

@pyuvm.test()
class ReadyValidDataInterfaceTest(pyuvm.uvm_test):
    def build_phase(self):
        self.env = ReadyValidDataInterfaceEnv("env", self)

    async def run_phase(self):
        self.raise_objection()
        cocotb.start_soon(cocotb.clock.Clock(cocotb.top.clk, 10, unit = "ns").start())
        ready_sequence = vulcan_eda.uvm.sequences.DataSequence.create("ready_sequence")
        ready_sequence.data_generator = vulcan_eda.uvm.generators.RandomBooleanGenerator(50)
        cocotb.start_soon(ready_sequence.start(self.env.downstream_agent.sequencer))
        data = [random.getrandbits(8) for _ in range(200)]
        for value in data:
            self.env.scoreboard.expected_data_analysis_fifo.analysis_export.write(value)
        for chunk in range(0, len(data), 50):
            valid_data_sequence = vulcan_eda.uvm.sequences.ValidDataSequence.create("valid_data_sequence")
            valid_data_sequence.data_generator = data[chunk:chunk + 50]
            await valid_data_sequence.start(self.env.upstream_agent.sequencer)
        await cocotb.triggers.ClockCycles(cocotb.top.clk, 2)
        handshakes = self.env.handshake_recorder.handshakes
        assert sum(handshakes) == len(data)
        assert any(first and second for first, second in zip(handshakes, handshakes[1:]))
        self.drop_objection()

def test_ready_valid_data_interface(build_dir):
    runner = cocotb_tools.runner.get_runner('ghdl')
    current_dir = pathlib.Path(__file__).parent

    runner.build(
        hdl_toplevel = "test_ready_valid_data_interface",
        sources = [current_dir / "test_ready_valid_data_interface.vhdl"],
        build_dir = build_dir,
        build_args = ["--std=08"]
    )

    runner.test(
        test_module = "test_ready_valid_data_interface",
        hdl_toplevel = "test_ready_valid_data_interface",
        hdl_toplevel_lang = "vhdl",
        build_dir = build_dir,
        test_dir = build_dir,
        test_args = ["--std=08"],
        plusargs = ["--fst=waves.fst"]
    )
