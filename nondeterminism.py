__all__ = [
    'nondeterministic', 'guess',
    'majority', 'maximize'
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


def is_success(result):
    return (result is not None and
            result is not False)


def first_success(results):
    if not results:
        return None
    return next(filter(is_success, results), results[0])
        

def majority(results):
    n = len(results)
    m = sum(1 for result in results
            if is_success(result))
    return 2 * m > n


def maximize(key):
    def max_with_key(iterable):
        return max(filter(is_success, iterable),
                   key=key, default=None)
    return max_with_key


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
