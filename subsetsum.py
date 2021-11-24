from nondeterminism import *


@nondeterministic
def subset_sum(values, target):
    subset = set()
    for x in values:
        if guess():
            subset.add(x)
    if sum(subset) == target:
        return subset


values = {1, 2, 3, 5}
for target in range(10):
    result = subset_sum(values, target)
    print(f'A subset {values} having sum {target} is:', result)
