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
            reject()
    accept()


vertices = {1, 2, 3}
edges = {(1,3), (3,2), (2,1)}

if hamiltonian(vertices, edges):
    print('The graph has a Hamiltonian cycle')
else:
    print('The graph has no Hamiltonian cycle')
