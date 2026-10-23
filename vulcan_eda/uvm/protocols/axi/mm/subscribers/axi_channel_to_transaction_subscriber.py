import collections

from vulcan_eda.uvm.protocols.axi.mm.data.axi_transaction import AxiTransaction
from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

class AxiChannelToTransactionSubscriber(TranslationSubscriber):
    channels = ("aw", "w", "b", "ar", "r")

    def build_phase(self):
        super().build_phase()
        self._write_addresses = collections.deque()
        self._write_data = collections.deque()
        self._write_beats = []
        self._read_addresses = collections.deque()
        self._read_beats = []

    def _translate(self, channel, lower_item):
        if channel == "aw":
            self._write_addresses.append(lower_item)
        elif channel == "w":
            self._write_beats.append(lower_item.data)
            if lower_item.last:
                self._write_data.append(tuple(self._write_beats))
                self._write_beats = []
        elif channel == "b":
            address = self._write_addresses.popleft()
            yield AxiTransaction(
                access=AxiTransaction.Access.WRITE,
                address=address.address,
                data=self._write_data.popleft(),
                num_beats=address.num_beats,
                id=address.id,
                burst=address.burst,
                response=lower_item.response)
        elif channel == "ar":
            self._read_addresses.append(lower_item)
        elif channel == "r":
            self._read_beats.append(lower_item.data)
            if lower_item.last:
                address = self._read_addresses.popleft()
                yield AxiTransaction(
                    access=AxiTransaction.Access.READ,
                    address=address.address,
                    data=tuple(self._read_beats),
                    num_beats=address.num_beats,
                    id=address.id,
                    burst=address.burst,
                    response=lower_item.response)
                self._read_beats = []
