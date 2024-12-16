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
    'success', 'majority', 'maximize', 'minimize'
]


import functools as ft
import multiprocessing as mp
import os


def is_success(x):
    return (x is not None and
            x is not False)


def success(lst):
    if not lst:
        return None
    x = lst[0]
    for x in lst:
        if is_success(x):
            return x
    return x


def majority(lst):
    n = len(lst)
    m = lst.count(True)
    return 2 * m > n


def identity(x):
    return x


def maximize(key=identity):
    def max_with_key(lst):
        return max((x for x in lst
                    if x is not None),
                   key=key, default=None)
    return max_with_key


def minimize(key=identity):
    def min_with_key(lst):
        return min((x for x in lst
                    if x is not None),
                   key=key, default=None)
    return min_with_key


class GuessError(RuntimeError):
    pass


GUESS_ERROR_MSG = (
    'can only guess in a nondeterministic context'
)


QUEUE = None


def nondeterministic(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        global QUEUE
        old_queue = QUEUE
        QUEUE = mp.SimpleQueue()
        if os.fork() == 0:
            result = function(*args, **kwargs)
            QUEUE.put(result)
            os._exit(0)
        else:
            os.wait()
            result = QUEUE.get()
            QUEUE = old_queue
            return result
    return wrapper


def guess(choices=(False, True), mode=success):
    if QUEUE is None:
        raise GuessError(GUESS_ERROR_MSG)
    if mode is minimize:
        mode = minimize()
    elif mode is maximize:
        mode = maximize()
    results = []
    for choice in choices:
        if os.fork() == 0:
            return choice
        else:
            os.wait()
            result = QUEUE.get()
            results.append(result)
    QUEUE.put(mode(results))
    os._exit(0)
