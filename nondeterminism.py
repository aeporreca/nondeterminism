__all__ = [
    'nondeterministic',
    'conondeterministic',
    'counting',
    'majority',
    'guess',
]


import functools as ft
import multiprocessing as mp
import os


# Main decorator, modify function so that it returns the result of
# accumulating by combine the return values of the computations of
# function, starting from initial and stopping when indicated by stop;
# finally, return apply post to the accumulator

def decorate(function, initial, combine, stop, post):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        queue = mp.SimpleQueue()
        queue.put(initial)                        # Initial accumulator
        if os.fork() == 0:
            result = function(*args, **kwargs)    # Actually execute function
            accum = queue.get()                   # Get the accumulated result
            accum = combine(accum, result)        # Update it
            queue.put(accum)                      # Replace the accumulator
            if stop(accum):                       # Found an acceptable result
                os._exit(0)                       # No need to go on
            else:
                os._exit(1)                       # Keep on computing
        else:
            os.wait()                             # No need to check the status
            return post(queue.get())              # Postprocessing
    return wrapper


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


# Combination functions

def _or(accum, result):
    return accum or result


def _and(accum, result):
    return accum and result


def add(accum, result):
    return accum + is_not_none_or_false(result)


def add_and_count(accum, result):
    return (accum[0] + is_not_none_or_false(result), accum[1] + 1)


# Stopping functions

def is_none_or_false(result):
    return result is None or result is False


def is_not_none_or_false(result):
    return result is not None and result is not False


def do_not_stop(result):
    return False


# Postprocessing functions

def identity(result):
    return result


def check_majority(result):
    return 2 * result[0] > result[1]


# Make the function nondeterministic

def nondeterministic(function):
    return decorate(function, None, _or, is_not_none_or_false, identity)


# Make the function conondeterministic

def conondeterministic(function):
    return decorate(function, True, _and, is_none_or_false, identity)


# Make the function return the number of accepting computations

def counting(function):
    return decorate(function, 0, add, do_not_stop, identity)


# Make the function return true iff the majority of its computations
# are accepting

def majority(function):
    return decorate(function, (0, 0), add_and_count,
                    do_not_stop, check_majority)
