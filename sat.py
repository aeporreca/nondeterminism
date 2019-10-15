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
