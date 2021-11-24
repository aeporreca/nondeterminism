import functools
import multiprocessing as mp
import os


# Guess one of the choices, halting as soon as a
# computation accepts (returns non-False, non-None)

def guess(choices = (False, True)):
    for choice in choices:
        if os.fork() == 0:
            return choice
        else:
            _, status = os.wait()
            if status >> 8 == 0:
                os._exit(0)
    os._exit(1)


# Nondeterminism decorator, modify function so that it returns
# a non-False, non-None result from an accepting computation

def nondeterministic(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        queue = mp.SimpleQueue()
        queue.put(None)
        if os.fork() == 0:
            result = function(*args, **kwargs)
            queue.get()
            queue.put(result)
            if (result is not None and
                    result is not False):
                os._exit(0)
            else:
                os._exit(1)
        else:
            os.wait()
            return queue.get()
    return wrapper
