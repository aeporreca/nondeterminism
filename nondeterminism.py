from __future__ import annotations


__all__ = [
    'nondeterministic', 'guess', 'coguess', 'Or', 'And',
    'Count', 'Majority', 'Maximize', 'Minimize', 'maximize',
    'minimize', 'is_success', 'is_failure', 'is_leaf', 'is_true'
]


import functools as ft
import multiprocessing as mp
import os

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Callable


def is_leaf(tree):
    return not isinstance(tree, CompTree)


def is_success(value):
    return (value is not None and
            value is not False)
        

def is_failure(value):
    return not is_success(value)


def is_true(x):
    return x is True


def identity(x):
    return x


def eval(result):
    if is_leaf(result):
        return result
    else:
        return result.eval()


def maximize(function):
    def partial(children):
        return Maximize(children, function)
    return partial


def minimize(function):
    def partial(children):
        return Minimize(children, function)
    return partial


@dataclass
class CompTree[T](ABC):
    children: list[CompTree[T] | T]

    @abstractmethod
    def eval(self):
        ...


class Or[T](CompTree):
    def eval(self):
        value = False
        for child in self.children:
            value = eval(child)
            if is_success(value):
                return value
        return value


class And[T](CompTree):
    def eval(self):
        value = True
        for child in self.children:
            value = eval(child)
            if is_failure(value):
                return value
        return value


class CountingCompTree[T](CompTree):
    def count(self, pred):
        cnt = pred(self)
        for child in self.children:
            if is_leaf(child):
                cnt += int(pred(child))
            else:
                cnt += child.count(pred)
        return cnt


class Count[T](CountingCompTree):
    def eval(self):
        return self.count(is_true)


class Majority[T](CountingCompTree):
    def eval(self):
        n_leaves = self.count(is_leaf)
        n_true = self.count(is_true)
        return 2 * n_true > n_leaves


@dataclass
class OptimizingCompTree[T](CompTree):
    function: Callable[[T], int | float] = identity

    def optimize(self, mode):
        values = map(eval, self.children)
        return mode(filter(is_success, values),
                    key=self.function, default=None)


@dataclass
class Maximize[T](OptimizingCompTree):
    def eval(self):
        return self.optimize(max)


@dataclass
class Minimize[T](OptimizingCompTree):
    def eval(self):
        return self.optimize(min)


RESULT: mp.SimpleQueue[Any] = mp.SimpleQueue()


def nondeterministic(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        if os.fork() == 0:
            result = function(*args, **kwargs)
            RESULT.put(result)
            os._exit(0)
        else:
            os.wait()
            tree = RESULT.get()
            return eval(tree)
    return wrapper


def guess(choices=(False, True), mode=Or):
    children = []
    for choice in choices:
        if os.fork() == 0:
            return choice
        else:
            os.wait()
            result = RESULT.get()
            children.append(result)
    RESULT.put(mode(children))
    os._exit(0)


def coguess(choices=(False, True)):
    return guess(choices, mode=And)
