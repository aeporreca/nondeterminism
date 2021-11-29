from nondeterminism import *


@nondeterministic
def composite(n):
    if n < 3:
        return False
    d = guess(range(2, n))
    return n % d == 0


def prime(n):
    return n > 1 and not composite(n)


maximum = 100
print(f'The primes below {maximum} are:')
for n in range(maximum):
    if prime(n):
        print(n)
