from nondeterminism import *


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
print('Is the formula is satisfiable?', result)
