# The `nondeterminism` Python library

> 🗞️ **News**
>
> 16 December 2024: `nondeterminism` 3.1.1 has been [released](https://github.com/aeporreca/nondeterminism/releases)! You can install it with `pip install nondeterminism`.

A Python library for writing nondeterministic algorithms (as in [nondeterministic Turing machines](https://en.wikipedia.org/wiki/Non-deterministic_Turing_machine), not directly related to randomised algorithms or to algorithms that just have inconsistent output due to bugs).

This library has been mostly designed for two purposes:

- as a teaching aid, in order to show that yeah, nondeterminism _per se_ doesn’t really exist, but you can still pretend it does[^abstraction], and students can get machine feedback when designing nondeterministic algorithms, instead of just writing pseudocode and crossing fingers;
- prototyping of nondeterministic algorithms for computer science research (which is actually how this project was born).

[^abstraction]: The same way that literally every day we pretend, with a straight face too, that `while` loops (or anything related to structured programming) do exist, even though our machines can only do conditional jumps. It’s just that nondeterminism is a less commonly used abstraction.

This library is not really suitable for production code; its implementation is based on [`fork(2)`](https://en.wikipedia.org/wiki/Fork_(system_call)), so it currently only runs on Unix variants (including Linux, macOS and, I suppose, Windows Subsystem for Linux) and is very slow for any nontrivial practical purpose.[^prolog] On the other hand, the implementation itself might also be of pedagogical interest as a nontrivial example of multiprocessing with shared memory.

[^prolog]: Notice that practical nondeterministic programming languages are actually available if you need them. The one I’m most familiar with is [Prolog](https://en.wikipedia.org/wiki/Prolog) which, by an amazing coincidence, was conceived by Colmerauer and Roussel precisely here in Marseille on the Luminy campus, where I ([AEP](https://aeporreca.org)) currently work. Prolog is amazing (and one of the inspirations behind this library), but its execution model is harder to reason about in terms of computational complexity (or, in any case, it is less familiar) than the usual imperative execution model. Prolog is also the subject of [the second-best joke about programming languages](http://james-iry.blogspot.com/2009/05/brief-incomplete-and-mostly-wrong.html). Besides Prolog, other things of interest in Marseille starting with P are [pastis](https://en.wikipedia.org/wiki/Pastis) and [panisses](https://fr.wikipedia.org/wiki/Panisse).

> ⚠️ **Warning**
>
> Although this library does exploit multiprocessing, it is not multiprocessing-safe itself! Don’t run multiple nondeterministic functions in parallel (although you _can_ call a nondeterministic function from another nondeterministic function, [oracle-like](https://en.wikipedia.org/wiki/Oracle_machine)).


## Contents

- [Installation](#installation)
- [License](#license)
- [Basic usage](#basic-usage)
  - [A nontrivial example: solving SAT](#a-nontrivial-example-solving-sat)
  - [Who exactly must be `@nondeterministic`?](#who-exactly-must-be-nondeterministic)
  - [Guessing non-`bool` values](#guessing-non-bool-values)
  - [Returning non-`bool` values](#returning-non-bool-values)
  - [A remark about infinite computations](#a-remark-about-infinite-computations)
- [More types of nondeterminism](#more-types-of-nondeterminism)
  - [Conondeterminism](#conondeterminism)
  - [Alternation](#alternation)
  - [Counting](#counting)
  - [Majority](#majority)
  - [Optimisation](#optimisation)
  - [Custom modes](#custom-modes)
- [Other examples](#other-examples)


## Installation

You can install this library via `pip install nondeterminism`. For the most recent changes, please check the [Git repository](https://github.com/aeporreca/nondeterminism), where you can also find the [bug tracker](https://github.com/aeporreca/nondeterminism/issues).


## License

In order to promote open research and teaching, the `nondeterminism` library is distributed under the [GNU AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html) license.


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

As a result, `is_satisfiable` returns `True` if and only if there is a satisfying assignment for the variables of `formula`. In other terms, the final result is `True` if and only if one possible computation of `is_satisfiable` (corresponding to a particular sequence of choices made by `guess`) returns `True`.


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
    return tuple(guess() for i in range(nvars))

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
@nondeterministic
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

However, a future version of the `nondeterminism` library _might_ implement [dovetailing](https://en.wikipedia.org/wiki/Dovetailing_(computer_science)) and allow `test6` to halt with a success. (On the other hand, the current behaviour on `test5` is correct, as this function must never halt.)

> ⚠️ **Warning**
> 
> If you execute a non-halting nondeterministic function like these (or a very slow one) in the Python interpreter in interactive mode, and you terminate it with a `ctrl-C`, this will probably leave the interpreter in an inconsistent state and you will be forced to restart it.[^restart]

[^restart]: This is another area where [improvement is needed](https://github.com/aeporreca/nondeterminism/issues/12), if this is possible at all.


## More types of nondeterminism

“Classic” nondeterminism as in the previous section allows you to solve all problems in [**NP**](https://en.wikipedia.org/wiki/NP_(complexity)) in (simulated) polynomial time, or the larger nondeterministic classes if you allow more time. The type of guesses we make in this type of algorithms can be called _existential_ or _disjunctive_, since the final result will be a success if and only if at least one of the computation paths is successful.

The `mode` keyword parameter to `guess` allows us to change the evaluation strategy. The default value of `mode` is `success` (i.e., `guess()` is the same as `guess(mode=success)`), which returns the first non-`None`, non-`False` result if any (or just the first result, if all are `None` or `False`). This is similar to the [`any`](https://docs.python.org/3/library/functions.html#any) Python builtin function, except that it considers values such as `0` and `[]` as successes, and it does not convert successful results to `True`. You can actually use `guess(mode=any)` if you’re only returning `bool` values.


### Conondeterminism

However, this is just the beginning. The dual of nondeterminism is “conondeterminism”, which uses _universal_ or _conjunctive_ choices. A conondeterministic algorithm is successful if and only if _all_ computation paths are successful; if just one of them fails, then the overall algorithm fails too. The corresponding complexity class is [**coNP**](https://en.wikipedia.org/wiki/Co-NP), assuming polynomial time, and the corresponding `mode` for guess is [`all`](https://docs.python.org/3/library/functions.html#all) (i.e., `guess(mode=all)`).

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


### Alternation

It turns out that you can freely mix existential and universal guesses (i.e., `guess(mode=any)` and `guess(mode=all)`) in your nondeterministic algorithms! This is called [alternation](https://en.wikipedia.org/wiki/Alternating_Turing_machine), and it’s extremely powerful: each time you switch from existential to universal guesses (or vice versa) you go one level up in the polynomial hierarchy [**PH**](https://en.wikipedia.org/wiki/Polynomial_hierarchy), and if the number of alternations can depend on the size of the input you can even solve all problems in [**PSPACE**](https://en.wikipedia.org/wiki/PSPACE#Other_characterizations) in polynomial time!

One of the standard **PSPACE**-complete problem is a variant of SAT called [TQBF](https://en.wikipedia.org/wiki/True_quantified_Boolean_formula) (aka QBF, or QSAT), where each variable is quantified… in an alternated fashion, of course. Given a Boolean formula `phi(x₀, x₁, …, xₙ₋₁)`, is it true that

> ∃`x₀` ∀`x₁` ∃`x₂` ⋯ $Q_{n-1}$`xₙ₋₁` `phi(x₀, x₁, …, xₙ₋₁)`

where $Q_i$ is ∃ if $i$ is even and ∀ if $i$ is odd?

Here is an (unboundedly) alternating algorithm for this problem:

```python
from inspect import signature
from nondeterminism import *

# Returns the number of parameters of function
def arity(function):
    return len(signature(function).parameters)

@nondeterministic
def is_q_valid(formula):
    n = arity(formula)
    x = tuple(guess(mode=any) if i % 2 == 0
              else guess(mode=all)
              for i in range(n))
    return formula(*x)
```

For instance, this gives us:

```pycon
>>> def phi(x, y):
...     return (x or y) and (x or not y)
... 
>>> is_q_valid(phi)
True
>>> def psi(x, y, z):
...     return x and not x and z and y
... 
>>> is_q_valid(psi)
False
```


### Counting

Counting algorithms return the number of successful computations. The corresponding polynomial-time complexity class is **#P** and the corresponding `mode` for `guess` is `sum`. Counting is also extremely powerful, since [you can solve the whole polynomial hierarchy in polynomial time](https://en.wikipedia.org/wiki/Toda%27s_theorem) if you have access to an oracle for a **#P**-complete problem!

One of the standard **#P**-complete problems is counting how many satisfying truth assignments exist for a given formula (let’s call this number the “satisfiability” of the formula):

```python
from inspect import signature
from nondeterminism import *

# Returns the number of parameters of function
def arity(function):
    return len(signature(function).parameters)

@nondeterministic
def satisfiability(formula):
    n = arity(formula)
    x = tuple(guess(mode=sum) for i in range(n))
    return formula(*x)
```

As an example:

```pycon
>>> def phi(x, y):
...     return (x or y) and (x or not y)
... 
>>> satisfiability(phi)
2
>>> def psi(x, y, z):
...     return x and not x and z and y
... 
>>> satisfiability(psi)
0
```


### Majority

Majority algorithms return `True` if and only if the (strict) majority of the computations are accepting. This is [as powerful as counting](https://en.wikipedia.org/wiki/Toda's_theorem)! The corresponding polynomial-time complexity class is [**PP**](https://en.wikipedia.org/wiki/PP_(complexity)) and the corresponding mode for `guess` is `majority`.

The standard **PP**-complete problem is [Majority-SAT](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem#Extensions_of_SAT), i.e., deciding whether the majority of assignments to a Boolean formula satisfy it:

```python
from inspect import signature
from itertools import product
from nondeterminism import *

# Returns the number of parameters of function
def arity(function):
    return len(signature(function).parameters)

@nondeterministic
def is_majority_satisfiable(formula):
    n = arity(formula)
    x = guess(product((False, True), repeat=n),
              mode=majority)
    return formula(*x)
```

Notice that this code, rather that making `n` consecutive majority guesses over `(False, True)`, only makes one `guess` over the `n`-th power of `(False, True)`, i.e., over the set of Boolean tuples of length `n`. This is necessary, since you want to maximise _once_ over this set, rather than maximising `n` times over `(False, True)`.

For instance:

```pycon
>>> def phi(x, y):
...     return (x or y) and (x or not y)
... 
>>> is_majority_satisfiable(phi)
False
>>> def psi(x, y, z):
...     return x or y
... 
>>> is_majority_satisfiable(psi)
True
```


## Optimisation

Optimisation algorithm not only give us a (usually non-`bool`-valued) solution to our problem, but one maximising (or minimising) a specific parameter. The corresponding polyonimial-time complexity class is [**OptP**](https://complexityzoo.net/Complexity_Zoo:O#optp), and the corresponding `mode` for `guess` is `maximize(key)` (resp., `minimize(key)`) where `key` is the value to be optimised across all non-`None` solutions.

As trivial examples, consider maximising or minimising the sum of binary tuples of a given length:

```python
from nondeterminism import *

@nondeterministic
def maximize_sum(n):
    return tuple(guess(range(2), mode=maximize(sum))
                 for i in range(n))

@nondeterministic
def minimize_sum(n):
    return guess(product(range(2), repeat=n),
                 mode=minimize(sum))
```

Observe how, unlike the majority example above, here you can either make consecutive guesses, or a single guess over the Cartesian product of all sets of choices.

```pycon
>>> maximize_sum(3)
(1, 1, 1)
>>> maximize_sum(1)
(1,)
>>> maximize_sum(0)
()
>>> minimize_sum(3)
(0, 0, 0)
>>> minimize_sum(2)
(0, 0)
>>> minimize_sum(0)
()
```

By default, the `maximize` and `minimize` modes optimise over the actual solutions themselves (i.e., the `key` is just the identity function), and return `None` if the set of solutions is empty. If using these optimisation modes this way you can drop the parentheses, e.g., you can write `guess(mode=maximize)` instead of `guess(mode=maximize())`.

For instance, we can re-implement Python’s `max` like this:

```python
@nondeterministic
def my_max(X):
    return guess(X, mode=maximize)
```

which gives us:

```pycon
>>> my_max(range(10))
9
>>> my_max(range(0))
>>> 
```


## Custom modes

You can define your own `mode`s for `guess` (e.g., something based on [leaf languages](https://en.wikipedia.org/wiki/Leaf_language)). A `mode` for `guess` is any function taking as input the list of results of the computation of your `@nondeterministic` function (either `bool` values, or whatever that function returns) and computes their combined result.

For instance, consider “parity algorithm”, which accept if and only if the number of accepting computations is odd. This corresponds to `xor`-ing together all the results:

```python
def xor(lst):
    result = False
    for x in lst:
        result = result is not x
    return result
```

Now you can just use `guess(mode=xor)` in your code. For instance, a funny way of checking if a number is a perfect square is to check if it has an odd number of divisors:

```python
from nondeterminism import *

@nondeterministic
def is_square(n):
    d = guess(range(1, n + 1), mode=xor)
    return n % d == 0
```

This gives:

```pycon
>>> [n for n in range(100) if is_square(n)]
[1, 4, 9, 16, 25, 36, 49, 64, 81]
```


## Other examples

You can find other examples for the `nondeterminism` library by looking for #TodaysNondeterministicAlgorithm on [Twitter](https://x.com/search?q=%23TodaysNondeterministicAlgorithm%20from%3Aaeporreca&src=typed_query&f=live) or [Bluesky](https://bsky.app/hashtag/TodaysNondeterministicAlgorithm?author=aeporreca.org). Notice that these might not be up-to-date with respect to the interface of the library.
