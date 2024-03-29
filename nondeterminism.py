import functools
import multiprocessing as mp
import os


# Nondeterminism decorator, modify function so that it returns
# a non-False, non-None result from an accepting computation

def nondeterministic(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        queue = mp.SimpleQueue()
        queue.put(None)                           # Always something to return
        if os.fork() == 0:
            result = function(*args, **kwargs)
            queue.get()                           # We only keep one result
            queue.put(result)                     # Replace the previous result
            if (result is not None and
                    result is not False):         # Found an acceptable result
                os._exit(0)                       # No need to go on
            else:
                os._exit(1)                       # Keep on searching
        else:
            os.wait()                             # No need to check the status
            return queue.get()
    return wrapper


# Guess one of the choices, halting as soon as a computation
# accepts (i.e., it returns non-False, non-None)

def guess(choices=(True, False)):
    result = 0
    for choice in choices:
        if os.fork() == 0:
            return choice
        else:
            _, status = os.wait()
            if status >> 8 == 0:                  # Found an acceptable result
                os._exit(0)                       # No need to go on
    os._exit(1)                                   # Exhausted all choices
