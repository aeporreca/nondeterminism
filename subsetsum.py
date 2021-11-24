from nondeterminism import *


@nondeterministic
def subset_sum(values, target):
    subset = set()
    for item in values:
        if guess():
            subset.add(item)
    if sum(subset) == target:
        return subset


values = {1, 4, 5}
for target in range(sum(values)+1):
    result = subset_sum(values, target)
    print(f'A subset of {values} having sum {target} is:', result)
