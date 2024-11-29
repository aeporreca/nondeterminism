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


# Default values for combine, shortcircuit, and postprocess for
# nondeterminize

def disjunction(x, y):
    return x or y

def is_success(x):
    return x is not None and x is not False

def identity(x):
    return x


# Modify function so that it returns the result of accumulating by
# combine the return values of the computations of function, starting
# from start and stopping early if indicated by shortcircuit; finally,
# return apply postprocess to the accumulator

def nondeterminize(function, combine=disjunction, start=None,
                   shortcircuit=is_success, postprocess=identity):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        queue = mp.SimpleQueue()
        queue.put(start)                          # Initial accumulator
        if os.fork() == 0:
            res = function(*args, **kwargs)       # Actually execute function
            acc = queue.get()                     # Get the accumulated result
            acc = combine(acc, res)               # Update it
            queue.put(acc)                        # Replace the accumulator
            if shortcircuit(acc):                 # We can stop here
                os._exit(0)                       # No need to go on
            else:
                os._exit(1)                       # Keep on computing
        else:
            os.wait()                             # No need to check the status
            return postprocess(queue.get())       # Optional postprocessing
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



# Nondeterministic decorator

def nondeterministic(function):
    return nondeterminize(function)


# Deterministic decorator: make the function... deterministic, i.e.,
# return the first result, successful or not (useless but it shows
# that this library covers this trivial case too)

def always(_):
    return True

def deterministic(function):
    return nondeterminize(function, shortcircuit=always)


# Conondeterministic decorator

def conjunction(x, y):
    return x and y

def is_failure(x):
    return x is None or x is False

def conondeterministic(function):
    return nondeterminize(function, combine=conjunction,
                          start=True, shortcircuit=is_failure)


# Counting decorator: make the function return the number of accepting
# computations

def add(acc, res):
    return acc + int(is_success(res))

def never(_):
    return False

def counting(function):
    return nondeterminize(function, combine=add,
                          start=0, shortcircuit=never)


# Majority decorator: make the function return true iff the majority
# of its computations are accepting

def add_counting(acc, res):
    return (acc[0] + int(is_success(res)), acc[1] + 1)

def check_majority(acc):
    return 2 * acc[0] > acc[1]

def majority(function):
    return nondeterminize(function, combine=add_counting,
                          start=(0, 0), shortcircuit=never,
                          postprocess=check_majority)
