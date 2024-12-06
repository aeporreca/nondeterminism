__all__ = [
    'nondeterministic', 'guess',
    'maximize', 'first_success'
]


import functools as ft
import multiprocessing as mp
import os


RESULT = mp.SimpleQueue()


def nondeterministic(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        if os.fork() == 0:
            result = function(*args, **kwargs)
            RESULT.put(result)
            os._exit(0)
        else:
            os.wait()
            result = RESULT.get()
            return result
    return wrapper


def first_success(lst):
    if not lst:
        return None
    return next(filter(None, lst), lst[0])
        

def guess(choices=(False, True), mode=first_success):
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


def maximize(key):
    def max_with_key(iterable):
        return max(filter(None, iterable),
                   key=key, default=None)
    return max_with_key
