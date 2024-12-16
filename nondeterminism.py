# nondeterminism - A Python library for nondeterministic algorithms
# Copyright (C) 2019, 2021, 2023, 2024 Antonio E. Porreca, Greg Hamerly

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


__all__ = [
    'nondeterministic', 'guess', 'GuessError',
    'success', 'RESULT'
]


import functools as ft
import itertools as it
import multiprocessing as mp
import os
import signal as sg


RESULT = []


def nondeterministic(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        RESULT.append(mp.SimpleQueue())
        if os.fork() == 0:
            result = function(*args, **kwargs)
            RESULT[-1].put(result)
            os._exit(0)
        else:
            os.wait()
            result = RESULT[-1].get()
            RESULT.pop()
            return result
    return wrapper


def is_success(x):
    return (x is not None and
            x is not False)


def is_failure(x):
    return not is_success(x)


def success(lst):
    if not lst:
        return None
    x = lst[0]
    for x in lst:
        if is_success(x):
            return x
    return x


class GuessError(RuntimeError):
    pass


GUESS_ERROR_MSG = \
    'can only guess in a nondeterministic context'


def timeout_handler(sig, _):
    print('timeout', flush=True)
    os._exit(0)


def setup_alarm(timeout):
    sg.signal(sg.SIGALRM, timeout_handler)
    sg.setitimer(sg.ITIMER_REAL, timeout)


QUANTUM = 0.1


def guess(choices=(False, True), mode=success, halt=is_success):
    if RESULT == []:
        raise GuessError(GUESS_ERROR_MSG)
    for steps in it.count(1):
        results = []
        nchoices = 0
        combined = None
        for choice in choices:
            if os.fork() == 0:
                setup_alarm(steps * QUANTUM)
                return choice
            else:
                nchoices += 1
                _, status = os.wait()
                code = os.WEXITSTATUS(status)
                if not RESULT[-1].empty():
                    result = RESULT[-1].get()
                    # inefficient
                    results.append(result)
                    combined = mode(results)
                    if halt(combined):
                        break
        if halt(combined) or len(results) == nchoices:
            break
    RESULT[-1].put(combined)
    os._exit(0)


# Tests

@nondeterministic
def test1():
    halt = guess()
    if halt:
        return True
    while True:
        pass


@nondeterministic
def test2():
    loop = guess()
    if not loop:
        return True
    while True:
        pass


@nondeterministic
def is_composite(n):
    if n < 2:
        return False
    d = guess(range(1, n))
    if d == 1:
        while True:
            pass
    else:
        return n % d == 0


import time
import random


@nondeterministic
def divisor(n):
    if n < 2:
        return False
    d = guess(range(2, n))
    time.sleep(random.random())
    if n % d == 0:
        return d


@nondeterministic
def find_natural(pred):
    naturals = it.count(0)
    n = guess(naturals)
    if pred(n):
        return n


@nondeterministic
def test3(n):
    x = guess(range(n))
    return False
