import pyuvm

from vulcan_eda.uvm.sequences.idle_sequence_item import IdleSequenceItem

class Driver(pyuvm.uvm_driver):
    def build_phase(self):
        self._interface = pyuvm.ConfigDB().get(self, "", "interface")

    async def run_phase(self):
        while True:
            await self._interface.write_edge()
            valid_item, sequence_item = self.seq_item_port.try_next_item()
            if valid_item:
                await sequence_item.item_ready.wait()
                if isinstance(sequence_item, IdleSequenceItem):
                    await self._interface.drive_idle()
                else:
                    await self._interface.drive_data(sequence_item.data)
                self.seq_item_port.item_done()
            else:
                await self._interface.drive_idle()
