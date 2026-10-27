import cocotb

class Handle:
    def __init__(self, width, value=0):
        self.width = width
        self.value = value
        self.value_change = cocotb.triggers.Event().wait()

    def __len__(self):
        return self.width
