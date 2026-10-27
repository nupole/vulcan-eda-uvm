import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.configs.agents.agent_config import AgentConfig
from vulcan_eda.uvm.monitors.monitor import Monitor

from tests.support.data import Unprintable

class Stop(Exception):
    pass

class Interface:
    def __init__(self, data):
        self.data = list(data)

    async def get_data(self):
        if not self.data:
            raise Stop()
        return self.data.pop(0)

def create_monitor(data, recording_subscriber):
    AgentConfig(Interface(data)).set(None, "monitor")
    monitor = Monitor.create("monitor", None)
    monitor.build_phase()
    monitor.analysis_port.connect(recording_subscriber.analysis_export)
    return monitor

def run(monitor):
    with pytest.raises(Stop):
        asyncio.run(monitor.run_phase())

def reported_messages(caplog, monitor):
    monitor.logger.addHandler(caplog.handler)
    try:
        run(monitor)
        monitor.report_phase()
    finally:
        monitor.logger.removeHandler(caplog.handler)
    return [record.getMessage() for record in caplog.records]

def test_publishes_monitored_data(recording_subscriber):
    monitor = create_monitor([1, 2], recording_subscriber)
    run(monitor)
    assert recording_subscriber.items == [1, 2]

def test_reports_a_summary_of_monitored_items(caplog, recording_subscriber):
    monitor = create_monitor([1, 2], recording_subscriber)
    assert reported_messages(caplog, monitor) == ["[SUMMARY] monitored 2 item(s)"]

def test_reports_monitored_items_at_high_verbosity(caplog, recording_subscriber):
    monitor = create_monitor([1, 2], recording_subscriber)
    monitor.set_report_verbosity(pyuvm.UVM_HIGH)
    assert reported_messages(caplog, monitor) == ["[MONITORED] monitored 1", "[MONITORED] monitored 2", "[SUMMARY] monitored 2 item(s)"]

def test_formats_no_monitored_item_below_high_verbosity(recording_subscriber):
    unprintable = Unprintable()
    run(create_monitor([unprintable], recording_subscriber))
    assert recording_subscriber.items == [unprintable]
