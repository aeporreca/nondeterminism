__all__ = ['nondeterministic', 'conondeterministic', 'guess']

import functools as ft
import multiprocessing as mp
import os


# Nondeterminism decorator, modify function so that it returns
# a non-False, non-None result from an accepting computation

def decorate(function, default, is_good):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        queue = mp.SimpleQueue()
        queue.put(default)                        # Always something to return
        if os.fork() == 0:
            result = function(*args, **kwargs)
            queue.get()                           # We only keep one result
            queue.put(result)                     # Replace the previous result
            if is_good(result):                   # Found an acceptable result
                os._exit(0)                       # No need to go on
            else:
                os._exit(1)                       # Keep on searching
        else:
            os.wait()                             # No need to check the status
            return queue.get()
    return wrapper


def is_not_none_or_false(result):
    return result is not None and result is not False


def nondeterministic(function):
    return decorate(function, None, is_not_none_or_false)


def is_none_or_false(result):
    return result is None or result is False


def conondeterministic(function):
    return decorate(function, True, is_none_or_false)


# Guess one of the choices, halting as soon as a computation
# accepts (i.e., it returns non-False, non-None)

def guess(choices=(False, True)):
    for choice in choices:
        if os.fork() == 0:
            return choice
        else:
            _, status = os.wait()
            if os.WEXITSTATUS(status) == 0:       # Found an acceptable result
                os._exit(0)                       # No need to go on
    os._exit(1)                                   # Exhausted all choices
