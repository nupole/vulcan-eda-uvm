import itertools

def take(generator, count):
    return list(itertools.islice(generator, count))
