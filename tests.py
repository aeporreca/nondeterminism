from nondeterminism import *


def formula(x, y, z):
    return ((x or y) and
            (y or z) and
            (not x or z))


@counting
def satisfiable(formula):
    x = guess()
    y = guess()
    z = guess()
    return formula(x, y, z)


@conondeterministic
def prime(n):
    if n < 2:
        return False
    d = guess(range(2, n))
    return n % d != 0
