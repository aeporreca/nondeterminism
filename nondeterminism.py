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

# Same thing, but modify function so that it returns the number
# of accepting computations (processes) on input (*args, **kwargs).

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


# Tests

if __name__ == '__main__':

    def formula(x, y, z):
        return ((x or y) and
                (y or z) and
                (not x or z))

    @nondeterministic
    def satisfiable(formula):
        x = guess()
        y = guess()
        z = guess()
        if formula(x, y, z):
            print(x, y, z)
            accept()
        else:
            reject()

    res = satisfiable(formula)
    print('The formula is satisfiable:', res)

    print()

    @nondeterministic
    def composite(n):
        d = guess(range(2, n - 1))
        if n % d == 0:
            print(d)
            accept()
        else:
            reject()

    def prime(n):
        return not composite(n)

    n = 14
    res = prime(n)
    print('The integer', n, 'is prime:', res)
