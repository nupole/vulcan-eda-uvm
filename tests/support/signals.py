class Handle:
    def __init__(self, width, value=0):
        self.width = width
        self.value = value

    def __len__(self):
        return self.width
