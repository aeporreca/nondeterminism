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


from math import isqrt


@conondeterministic
def is_prime(n):
    if n < 2:
        return False
    d = guess(range(2, isqrt(n) + 1))
    return n % d != 0
