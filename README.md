# nondeterminism

A Python library for writing nondeterministic algorithms (as in [nondeterministic Turing machines](https://en.wikipedia.org/wiki/Non-deterministic_Turing_machine), not directly related to randomised algorithms or to algorithms that just have inconsistent output due to bugs).

This library has been mostly designed for two purposes:

- as a teaching aid, in order to show that yeah, nondeterminism _per se_ doesn’t really exist, but you can still pretend it does[^abstraction], and students can get machine feedback when designing nondeterministic algorithms, instead of just writing pseudocode and crossing fingers;
- prototyping of nondeterministic algorithms for computer science research (which is actually how this project was born).

[^abstraction]: The same way that literally every day we pretend, with a straight face too, that `while` loops (or anything related to structured programming) do exist, even though our machines can only do conditional jumps. It’s just that nondeterminism is a less commonly used abstraction.

This library is not really suitable for production code; its implementation is based on [`fork(2)`](https://en.wikipedia.org/wiki/Fork_(system_call)), so it currently only runs on Unix variants (including Linux, macOS and, I suppose, Windows Subsystem for Linux) and is very slow for any nontrivial practical purpose.[^prolog] On the other hand, the implementation itself might also be of pedagogical interest as a nontrivial example of multiprocessing with shared memory.

[^prolog]: Notice that practical nondeterministic programming languages are actually available if you need them. The one I’m most familiar with is [Prolog](https://en.wikipedia.org/wiki/Prolog) which, by an amazing coincidence, was conceived by Colmerauer and Roussel precisely here in Marseille on the Luminy campus, where I (AEP) currently work. Prolog is amazing (and one of the inspirations behind this library), but its execution model is harder to reason about in terms of computational complexity (or, in any case, it is less familiar) than the usual imperative execution model. Prolog is also the subject of [the second-best joke about programming languages](http://james-iry.blogspot.com/2009/05/brief-incomplete-and-mostly-wrong.html). Besides Prolog, other things of interest in Marseille starting with P are [pastis](https://en.wikipedia.org/wiki/Pastis) and [panisses](https://fr.wikipedia.org/wiki/Panisse).


## Contents

- [Basic usage](#basic-usage)
  - [A nontrivial example: solving SAT](#a-nontrivial-example-solving-sat)
  - [Who exactly must be `@nondeterministic`?](#who-exactly-must-be-nondeterministic)
  - [Guessing non-`bool` values](#guessing-non-bool-values)
  - [Returning non-`bool` values](#returning-non-bool-values)
  - [A remark about infinite computations](#a-remark-about-infinite-computations)
- [More types of nondeterminism](#more-types-of-nondeterminism)
  - [Conondeterminism](#conondeterminism)

## Basic usage

You declare a function nondeterministic by using the `@nondeterministic` decorator and call `guess` inside it (or in a function called by it) in order to get a `True` or a `False`. Which one? Well, `guess` _wants_ your nondeterministic function to succeed, so it will return a result that allows that, if it is possible at all.

As a trivial example, consider this:

```python
from nondeterminism import *

@nondeterministic
def test1():
    x = guess()
    return x
```

The only way for `test` to succeed (i.e., return `True`) is if `x` is `True`, so `guess` will necessarily return `True`:

```pycon
>>> test1()
True
```

Now consider this slight variation:

```python
from nondeterminism import *

@nondeterministic
def test2():
    x = guess()
    return not x
```

In this case, `test2` needs `x` to be `False` in order to succeed, and `guess` will happily oblige:

```pycon
>>> test2()
True
```

However, consider this third trivial example:

```python
from nondeterminism import *

@nondeterministic
def test3():
    x = guess()
    return x and not x
```

Here `guess` cannot make `test3` succeed, since `x and not x` is a contradiction. As a consequence, `guess` will return whatever value (the actual value is unspecified) and let `test3` fail:

```pycon
>>> test3()
False
```


### A nontrivial example: solving SAT

By generalising the previous, trivial examples we can write a [SAT solver](https://en.wikipedia.org/wiki/SAT_solver) in just a few lines of code:

```python
from inspect import signature
from nondeterminism import *

# Number of parameters of function
def arity(function):
    return len(signature(function).parameters)

@nondeterministic
@nondeterministic
def is_satisfiable(formula):
    n = arity(formula)
    x = tuple(guess() for i in range(n))
    return formula(*x)
```

The `is_satisfiable` function makes one guess per variable, then evaluates the input formula on the truth assignment obtained this way:

```pycon
>>> def phi(x, y):
...     return (x or y) and (x or not y)
... 
>>> is_satisfiable(phi)
True
>>> def psi(x, y, z):
...     return x and not x and z and y
... 
>>> is_satisfiable(psi)
False
```

As a result, `is_satisfiable` returns `True` if and only if there is a satisfying assignment for the variables of `formula`. In other terms, the final result is `True` if and only if one possible computation of `is_satisfiable` (corresponding to a particular sequence of choices by made `guess`) returns `True`.


### Who exactly must be `@nondeterministic`?

The function calling `guess` need not be declared `@nondeterministic` itself, as long as it is called by a `@nondeterministic` function (or by a function called by a `@nondeterministic` function, or so on, recursively).

For instance, you can rewrite the SAT solver by separating the actual guessing this way, which might even be more readable and reusable:

```python
from inspect import signature
from nondeterminism import *

# Number of parameters of function
def arity(function):
    return len(signature(function).parameters)

def guess_assignment(nvars):
    return [guess() for i in range(nvars)]

@nondeterministic
def is_satisfiable(formula):
    n = arity(formula)
    x = guess_assignment(n)
    return formula(*x)
```

Notice that `guess_assignment` is _not_ declared `@nondeterministic`, while `is_satisfiable` is: it’s the latter function that must return `True` if and only if it has an accepting computation, not `guess_assignment`.

However, you can _only_ call `guess` from a nondeterministic context, meaning that either the function calling `guess`, or recursively one of the functions calling it, must have been declared `@nondeterministic`. For instance, the following code

```python
from nondeterminism import *

def test4():
    return guess()
```

produces a `GuessError` at runtime:

```pycon
>>> test4()
Traceback (most recent call last):
[...]
nondeterminism.GuessError: can only guess in a nondeterministic context
```


### Guessing non-`bool` values

By default, `guess` returns a `bool` value, either `False` or `True`; but by giving it an optional iterable (such as a `list` or a `set`) as a parameter, you can guess anything you like.

For instance, the following code solves the [Hamiltonian cycle problem](https://en.wikipedia.org/wiki/Hamiltonian_path_problem) by guessing a permutation of the vertices of the input graph:

```python
def is_hamiltonian(G):
    (V, E) = G
    n = len(V)
    V = V.copy()
    p = []
    while V:
        v = guess(V)
        p.append(v)
        V.remove(v)
    for i in range(n):
        if (p[i], p[(i+1)%n]) not in E:
            return False
    return True
```

This produces:

```pycon
>>> V = {1, 2, 3}
>>> E = {(1, 3), (3, 1), (3, 2), (2, 1)}
>>> G = (V, E)
>>> is_hamiltonian(G)
True
```


### Returning non-`bool` values

Nondeterministic functions returning `False` or `True` are all fine and dandy, but what if you want to know, e.g., an actual assignment satisfying your formula? Well, you just `return` it!

```python
from inspect import signature
from nondeterminism import *

# Returns the number of parameters of function
def arity(function):
    return len(signature(function).parameters)

@nondeterministic
def satisfy(formula):
    n = arity(formula)
    x = tuple(guess() for i in range(n))
    if formula(*x):
        return x
```

If no satisfying assignment is found, you get `None` (invisible in the Python interpreter) as a result:

```pycon
>>> def phi(x, y):
...     return (x or y) and (x or not y)
... 
>>> satisfy(phi)
(True, False)
>>> def psi(x, y, z):
...     return x and not x and z and y
... 
>>> satisfy(psi)
>>> 
```


### A remark about infinite computations

Often nondeterministic algorithms are defined in such a way that even infinite (non-halting) computation paths are allowed, as long as [at least one halting path exists](https://en.wikipedia.org/wiki/Nondeterministic_Turing_machine#Resolution_of_multiple_rules). This is not currently allowed by the `nondeterminism` library: if a sequence of choices leads us to a non-terminating computation, the nondeterministic function will not halt.

For instance, with the current implementation neither of the following `test5` and `test6` functions halts:

```python
from nondeterminism import *

@nondeterministic
def test5():
    while True:
        pass

@nondeterministic
def test6():
    halt = guess()
    if halt:
        return True
    else:
        while True:
            pass
```

However, a future version of the `nondeterminism` library _might_ implement [dovetailing](https://en.wikipedia.org/wiki/Dovetailing_(computer_science)) and allow `test5` to halt with a success. (On the other hand, the current behaviour on `test5` is correct, it must never halt.)

> [!WARNING]
> If you execute a non-halting nondeterministic function like these (or a very slow one) in the Python interpreter in interactive mode, and you terminate it with a `ctrl-C`, this will probably leave the interpreter in an inconsistent state and you will be forced to restart it.[^restart]

[^restart]: This is another area where [improvement is needed](https://github.com/aeporreca/nondeterminism/issues/12), if this is possible at all.


## More types of nondeterminism

“Classic” nondeterminism as in the previous section allows you to solve all problems in [**NP**](https://en.wikipedia.org/wiki/NP_(complexity)) in (simulated) polynomial time, or the larger nondeterministic classes if you allow more time. The type of guesses we make in this type of algorithms can be called _existential_ or _disjunctive_, since the final result will be a success if and only if at least one of the computation paths is successful.

The `mode` keyword parameter to `guess` allows us to change the evaluation strategy. The default value of `mode` is `success` (i.e., `guess()` is the same as `guess(mode=success)`), which returns the first non-`None`, non-`False` result. This is analogous to the [`any`](https://docs.python.org/3/library/functions.html#any) Python builtin function, except that it considers values such as `0` and `[]` as successes, and it does not convert to `True` successful results. You can actually use `guess(mode=any)` if you’re only returning `bool` values.

### Conondeterminism

However, this is just the beginning. The dual of nondeterminism is “conondeterminism”, which uses _universal_ or _conjunctive_ choices. A conondeterministic algorithm is successful if and only if _all_ computation paths are successful; if just one of them fails, then the overall algorithm fails too. The corresponding complexity class is [**coNP**](https://en.wikipedia.org/wiki/Co-NP), assuming polynomial time. The corresponding `mode` for guess is [`all`](https://docs.python.org/3/library/functions.html#all) (i.e., `guess(mode=all)`).

A classic example of conondeterministic algorithm is primality testing[^primes]: assuming `n >= 2`, you guess a nontrivial divisor, and if it does indeed divide `n`, then it’s not a prime.

[^primes]: Of course, since 2002 we know that primality can actually be tested in _deterministic_ polynomial time with the [AKS algorithm](https://en.wikipedia.org/wiki/AKS_primality_test).

```python
from nondeterminism import *

@nondeterministic
def is_prime(n):
    if n < 2:
        return False
    d = guess(range(2, n), mode=all)
    return n % d != 0
```

Here is a list of the primes below 50:

```pycon
>>> [n for n in range(50) if is_prime(n)]
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
```
