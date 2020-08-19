from os import fork, wait, _exit
from functools import wraps


# Modify function so that it returns True when there is at least one
# accepting computation (process) on input (*args, **kwargs).

def nondeterministic(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if fork() == 0:
            function(*args, **kwargs)
        else:
            result = wait()[1] >> 8
            return result != 0
    return wrapper


# Guess one of the choices

def guess(choices = (True, False)):
    result = 0
    for choice in choices:
        if fork() == 0:
            return choice
        else:
            result = wait()[1] >> 8
            if result != 0:
                break
    _exit(result)


# Accept

def accept():
    _exit(1)


# Reject

def reject():
    _exit(0)
