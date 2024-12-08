__all__ = [
    'nondeterministic', 'guess', 'GuessError',
    'success', 'majority', 'maximize', 'minimize'
]


import functools as ft
import multiprocessing as mp
import os


RESULT = None


def nondeterministic(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        global RESULT
        RESULT = mp.SimpleQueue()
        if os.fork() == 0:
            result = function(*args, **kwargs)
            RESULT.put(result)
            os._exit(0)
        else:
            os.wait()
            result = RESULT.get()
            RESULT = None
            return result
    return wrapper


def is_success(x):
    return (x is not None and
            x is not False)


def success(lst):
    if not lst:
        return None
    x = lst[0]
    for x in lst:
        if is_success(x):
            return x
    return x


def majority(lst):
    n = len(lst)
    m = lst.count(True)
    return 2 * m > n


def identity(x):
    return x


def maximize(key=identity):
    def max_with_key(lst):
        return max((x for x in lst
                    if x is not None),
                   key=key, default=None)
    return max_with_key


def minimize(key=identity):
    def min_with_key(lst):
        return min((x for x in lst
                    if x is not None),
                   key=key, default=None)
    return min_with_key


class GuessError(RuntimeError):
    pass


GUESS_ERROR_MSG = \
    'can only guess in a nondeterministic context'


def guess(choices=(False, True), mode=success):
    if RESULT is None:
        raise GuessError(GUESS_ERROR_MSG)
    results = []
    for choice in choices:
        if os.fork() == 0:
            return choice
        else:
            os.wait()
            result = RESULT.get()
            results.append(result)
    RESULT.put(mode(results))
    os._exit(0)
