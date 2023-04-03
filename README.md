# nondeterminism

A Python 3 library for writing nondeterministic algorithms, as in [nondeterministic Turing machines](https://en.wikipedia.org/wiki/Non-deterministic_Turing_machine).

This library is mostly designed for teaching purposes (providing executable pseudocode for nondeterministic algorithms), and is not suitable for production code (the implementation is based on `fork(2)`, so currently this code only runs on Unix, and is not optimised).

Here is, as an exemple, a nondeterministic algorithm for checking if a graph admits a Hamiltonian cycle.

```python
from nondeterminism import nondeterministic, guess


@nondeterministic
def hamiltonian(vertices, edges):
    vertices = vertices.copy()
    n = len(vertices)
    perm = []
    while vertices:
        v = guess(vertices)
        perm.append(v)
        vertices.remove(v)
    for i in range(n):
        if (perm[i], perm[(i + 1) % n]) not in edges:
            return False
    return True


vertices = {1, 2, 3}
edges = {(1, 3), (3, 1), (3, 2), (2, 1)}
result = hamiltonian(vertices, edges)
print('Does the graph have a Hamiltonian cycle?', result)
```

Each function using nondeterminism (i.e., calling `guess()`) must be decorated with the `@nondeterministic` decorator.

The function `guess()` takes as an optional argument an iterable object, such as a `list` or a `set`, and defaults to returning either `True` or `False`, as shown by the following example (solving SAT over three variables):

```python
from nondeterminism import nondeterministic, guess


@nondeterministic
def satisfiable(formula):
    x = guess()
    y = guess()
    z = guess()
    return formula(x, y, z)


def formula(x, y, z):
    return ((x or y) and
            (y or z) and
            (not x or z))


result = satisfiable(formula)
print('Is the formula satisfiable?', result)
```

Notice that only nondeterministic functions need to be decorated with `@nondeterministic`, as shown by the following code for checking the primality of natural numbers:

```python
from nondeterminism import nondeterministic, guess


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
```

You can also return non-Boolean values. In that case, the first result different from `False` and `None` is returned. Here we search for a subset of the `values` having sum `target`, and return the subset itself rather than just `True` if it exists:

```python
from nondeterminism import nondeterministic, guess


@nondeterministic
def subset_sum(values, target):
    subset = set()
    for item in values:
        if guess():
            subset.add(item)
    if sum(subset) == target:
        return subset


values = {1, 4, 5}
for target in range(sum(values) + 1):
    result = subset_sum(values, target)
    print(f'A subset of {values} having sum {target} is: {result}')
```
