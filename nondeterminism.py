# WARNING: Broken code!

import functools as ft
import itertools as it
import multiprocessing as mp
import os
import signal as sg


# Exit codes used below

SUCCESS = 0
FAILURE = 1
TIMEOUT = 2


# Nondeterminism decorator, modify function so that it returns
# a non-False, non-None result from an accepting computation

def nondeterministic(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        queue = mp.SimpleQueue()
        queue.put(None)                           # Always something to return
        if os.fork() == 0:
            result = function(*args, **kwargs)
            queue.get()                           # We only keep one result
            queue.put(result)                     # Replace the previous result
            if (result is not None and
                    result is not False):         # Found an acceptable result
                os._exit(SUCCESS)                 # No need to go on
            else:
                os._exit(FAILURE)                 # Keep on searching
        else:
            os.wait()                             # No need to check the status
            return queue.get()
    return wrapper


# Halt with a TIMEOUT exit code

def timeout_handler(sig, _):
    os._exit(TIMEOUT)


# Set up an alarm after timeout seconds

def setup_alarm(timeout):
    sg.signal(sg.SIGALRM, timeout_handler)
    sg.setitimer(sg.ITIMER_REAL, timeout)


# Iterate over all pairs (n, x) for n a positive integer
# and x in choices

def dovetail(choices):
    choices, copy = it.tee(choices)
    try:
        next(copy)
    except StopIteration:
        return                                    # choices is empty
    for n in it.count(1):
        choices, copy = it.tee(choices)
        steps = reversed(range(1, n + 1))
        yield from zip(steps, copy)


# Time quantum in seconds

QUANTUM = 0.1


# Guess one of the choices, halting as soon as a computation
# accepts (i.e., it returns non-False, non-None)

def guess(choices=(False, True)):
    print('in guess')
    old_steps = 0
    for steps, choice in dovetail(choices):
        print('> trying', steps, choice)
        n_halted = 0
        if os.fork() == 0:
            setup_alarm(steps * QUANTUM)
            return choice
        else:
            _, status = os.wait()
            code = os.WEXITSTATUS(status)
            if code == SUCCESS:
                os._exit(SUCCESS)
            if code != TIMEOUT:
                n_halted += 1
        if steps != old_steps and n_halted == steps:
            os._exit(FAILURE)
        else:
            old_steps = steps
    os._exit(FAILURE)
