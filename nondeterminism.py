import functools as ft
import itertools as it
import multiprocessing as mp
import os
import signal as sig


# BROKEN CODE!


SUCCESS = 0                     # Halted and found a solution
FAILURE = 1                     # Not found a solution (yet?)


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
                print(os.getpid(), 'succeded')
                os._exit(SUCCESS)                 # No need to go on
            else:
                print(os.getpid(), 'failed')
                os._exit(FAILURE)                 # Keep on searching
        else:
            os.wait()                             # No need to check the status
            return queue.get()
    return wrapper


def dovetail(iterator):
    iterator, copy = it.tee(iterator)
    try:
        next(copy)
    except StopIteration:
        return
    for n in it.count(1):
        iterator, copy = it.tee(iterator)
        for x in it.islice(copy, n):
            yield n, x


def timeout(sig, frame):
    print(os.getpid(), 'timeout')
    os._exit(FAILURE)


QUANTUM = 0.00001               # Time quantum in seconds


# Guess one of the choices, halting as soon as a computation
# accepts (i.e., it returns non-False, non-None)

def guess(choices=(False, True)):
    for steps, choice in dovetail(choices):
        print('here', flush=True)
        pid = os.fork()
        if pid == 0:
            sig.signal(sig.SIGVTALRM, timeout)
            sig.setitimer(sig.ITIMER_VIRTUAL, steps * QUANTUM)
            print(os.getpid(), 'guessed', choice)
            return choice
        else:
            print('waiting for', pid)
            pid, status = os.wait()
            print(pid, 'arrived')
            code = os.WEXITSTATUS(status)
            if code == SUCCESS:                     # Found an acceptable result
                print('my child', pid, 'succeeded!')
                os._exit(SUCCESS)                   # No need to go on
    os._exit(FAILURE)                               # Exhausted all choices
