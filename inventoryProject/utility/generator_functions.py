import random


def generate_unique_key(length, prepend=None):
    prepend = '' if prepend is None else str(prepend)
    random_separator = ''.join(random.choice('0123456789') for i in range(2))
    random_string = ''.join(random.choice('0123456789') for i in range(length-len(prepend)-len(random_separator)))
    return (prepend + random_separator + random_string)[:length]


def str_to_bool(value):
    return value.lower() == 'true'