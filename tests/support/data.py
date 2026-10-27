class Unprintable:
    def __str__(self):
        raise AssertionError("formatted a message that was filtered out")

    __repr__ = __str__
