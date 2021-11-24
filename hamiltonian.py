from nondeterminism import *


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
        if (perm[i], perm[(i+1)%n]) not in edges:
            return False
    return True


vertices = {1, 2, 3}
edges = {(1, 3), (3, 1), (3, 2), (2, 1)}
result = hamiltonian(vertices, edges)
print('Does the graph has a Hamiltonian cycle?', result)
