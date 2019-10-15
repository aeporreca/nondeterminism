# nondeterminism

Python 3 library for writing nondeterministic algorithms.

This library is mostly designed for teaching purposes (providing executable pseudocode for nondeterministic algorithms), and is not suitable for production code (the implementation is based on fork(2), so currently this code only runs on Unix, and is not optimised).

Here is, as an exemple, a nondeterministic algorithm for checking if a graph admits a Hamiltonian cycle (see the file `hamilton.py`)

```python
from nondeterminism import *

@nondeterministic
def hamiltonian(vertices, edges):
    n = len(vertices)
    perm = []
    for i in range(n):
        v = guess(vertices)
        perm.append(v)
    for v in vertices:
        if perm.count(v) != 1:
            reject()
    for i in range(n):
        if (perm[i], perm[(i+1)%n]) not in edges:
            reject()
    accept()


vertices = {1, 2, 3}
edges = {(1,3), (3,2), (2,1)}

if hamiltonian(vertices, edges):
    print('The graph has a Hamiltonian cycle')
else:
    print('The graph has no Hamiltonian cycle')

```

For the moment only Boolean-valued functions are supported; each function using nondeterminism (i.e., calling `guess()`, `accept()` and `reject()`) must be decorated with the `@nondeterministic` decorator. Every time you would return `True`, you must instead `accept()`, and similarly each `return False` must be replaced by a call to `reject()`.

The function `guess()` takes as an optional argument an iterable object, such as a `list` or a `set`, and defaults to returning either `True` or `False`, as shown by the following example (solving SAT over three variables, see `sat.py`):

```python
from nondeterminism import *

@nondeterministic
def satisfiable(formula):
    x = guess()
    y = guess()
    z = guess()
    if formula(x, y, z):
        accept()
    else:
        reject()

def formula(x, y, z):
    return ((x or y) and
            (y or z) and
            (not x or z))

if satisfiable(formula):
    print('The formula is satisfiable')
else:
    print('The formula is not satisfiable')
```

Notice that *only* nondeterministic functions must be decorated with `@nondeterministic`, as shown by the following code for checking the primality of natural numbers (see `prime.py`):

```python
from nondeterminism import *

@nondeterministic
def composite(n):
    d = guess(range(2, n - 1))
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
```
