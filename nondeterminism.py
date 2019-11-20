from os import fork, wait, _exit
from functools import wraps
from multiprocessing import Value


# _result is an unsigned long variable shared among processes.

_result = Value('L', 0)


# Modify function so that it returns True when there is at least one
# accepting computation (processe) on input (*args, **kwargs).

def nondeterministic(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if fork() == 0:
            function(*args, **kwargs)
        else:
            wait()
            return _result.value > 0
    return wrapper


# Only one process runs at a time; this is actually required,
# since _result can only contain one value. This also avoids
# the need to acquire a lock before manipulating _result.

def guess(choices = (True, False)):
    for choice in choices:
        if fork() == 0:
            return choice
        else:
            wait()
            if _result.value: # break early if this branch accepted
                break
    _exit(0)


# Accept

def accept():
    _result.value = 1
    _exit(0)


# Reject

def reject():
    _result.value = 0
    _exit(0)
