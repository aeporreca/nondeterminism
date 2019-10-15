from nondeterminism import *

@nondeterministic
def composite(n):
    d = guess(range(2, n))
    if n % d == 0:
        accept()
    else:
        reject()

def prime(n):
    if n < 2:
        return False
    else:
        return not composite(n)

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for n in numbers:
    if prime(n):
        print('The integer', n, 'is prime')
    else:
        print('The integer', n, 'is not prime')
