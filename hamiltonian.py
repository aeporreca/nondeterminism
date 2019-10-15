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
