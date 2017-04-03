import random


def generate_unique_key(length, prepend=None):
    prepend = '' if prepend is None else prepend
    random_separator = ''.join(random.choice('GHIJKLMNOPQRSTUVWXYZ') for i in range(2))
    random_string = ''.join(random.choice('0123456789ABCDEF') for i in range(length-len(prepend)-len(random_separator)))
    return (prepend + random_separator + random_string)[:length]
