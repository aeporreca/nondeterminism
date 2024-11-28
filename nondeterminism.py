__all__ = [
    'deterministic',
    'nondeterministic',
    'conondeterministic',
    'counting',
    'majority',
    'guess',
]


import functools as ft
import multiprocessing as mp
import os
import operator as op


# Default combine, inject and shortcircuit for nondeterminize

def disjunction(x, y):
    return x or y


def identity(x):
    return x


def never(x):
    return False


# General decorator, modify function so that it returns the result of
# accumulating by combine the injection of the return values of the
# computations of function, starting from start and stopping when
# shorcircuit by stop; finally, return postprocess applied to the
# accumulator

def nondeterminize(function, combine=disjunction, start=None,
                   inject=identity, shortcircuit=never,
                   postprocess=identity):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        queue = mp.SimpleQueue()
        queue.put(start)                          # Initial accumulator
        if os.fork() == 0:
            result = function(*args, **kwargs)    # Actually execute function
            acc = queue.get()                     # Get the accumulator
            acc = combine(acc, inject(result))    # Update it
            print(acc)
            queue.put(acc)                        # Replace the accumulator
            if shortcircuit(acc):                 # Stop here
                os._exit(0)                       # No need to go on
            else:
                os._exit(1)                       # Keep on computing
        else:
            os.wait()                             # No need to check the status
            return postprocess(queue.get())       # Postprocessing
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


# Deterministic decorator

def always(x):
    return True


def deterministic(function):
    return nondeterminize(function, shortcircuit=always)


# Noneterministic decorator

def is_success(x):
    return x is not None and x is not False


def nondeterministic(function):
    return nondeterminize(function, shortcircuit=is_success)


# Cononeterministic decorator

def conjunction(x, y):
    return x and y


def is_failure(x):
    return x is None or x is False


def conondeterministic(function):
    return nondeterminize(function, combine=conjunction,
                          start=True, shortcircuit=is_failure)


# Counting decorator

def binarize(x):
    return int(x is not None and x is not False)


def counting(function):
    return nondeterminize(function, combine=op.add,
                          start=0, inject=binarize)


# Majority decorator

def tuple_add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def binarize_and_count(x):
    return (binarize(x), 1)


def check_majority(acc):
    return 2 * acc[0] > acc[1]


def majority(function):
    return nondeterminize(function, combine=tuple_add,
                          start=(0, 0), inject=binarize_and_count,
                          postprocess=check_majority)
