from os import fork, wait, _exit
from multiprocessing import Value

# _result is an unsigned long variable shared among processes.

_result = Value('L', 0)

# Count how many times function accepts on input (*args, **kwargs).

def _count(function, *args, **kwargs):
    if fork() == 0:
        function(*args, **kwargs)
    else:
        wait()
        res = _result.value
        _result.value = 0       # Probably useless.
        return res

# Modify function so that it returns True when there is at least one
# accepting computation (processe) on input (*args, **kwargs).

def nondeterministic(function):
    def wrapper(*args, **kwargs):
        return _count(function, *args, **kwargs) > 0
    wrapper.__name__ = function.__name__
    return wrapper

# Only one process runs at a time; this is actually required,
# since _result can only contain one value. This also avoids
# the need to acquire a lock before manipulating _result.

def guess(choices = [False, True]):
    total = 0
    for choice in choices:
        if fork() == 0:
            return choice
        else:
            wait()
            total += _result.value
            _result.value = 0
    _result.value = total
    _exit(0)

# Accept

def accept():
    _result.value = 1
    _exit(0)

# Reject

def reject():
    _result.value = 0
    _exit(0)
