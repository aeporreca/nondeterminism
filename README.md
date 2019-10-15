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
    print('The graph has a Hamiltonian cycle.')
else:
    print('The graph has no Hamiltonian cycle.')

```
