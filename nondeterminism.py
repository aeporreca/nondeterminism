from __future__ import annotations


__all__ = [
    'nondeterministic', 'guess', 'coguess',
    'Or', 'And', 'Count', 'Majority', 'maximize', 'minimize',
    'is_success', 'is_failure', 'is_leaf', 'is_true',
]


import functools as ft
import multiprocessing as mp
import os

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Callable


def is_leaf(tree):
    return not isinstance(tree, CompTree)


def is_success(value):
    return (value is not None and
            value is not False)
        

def is_failure(value):
    return (value is None or
            value is False)


def is_true(x):
    return x is True


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


class Or(CompTree):
    def eval(self):
        value = False
        for child in self.children:
            value = eval(child)
            if is_success(value):
                return value
        return value


class And(CompTree):
    def eval(self):
        value = True
        for child in self.children:
            value = eval(child)
            if is_failure(value):
                return value
        return value


class CountingCompTree(CompTree):
    def count(self, pred):
        cnt = pred(self)
        for child in self.children:
            if is_leaf(child):
                cnt += int(pred(child))
            else:
                cnt += child.count(pred)
        return cnt


class Count(CountingCompTree):
    def eval(self):
        return self.count(is_true)


class Majority(CountingCompTree):
    def eval(self):
        n_leaves = self.count(is_leaf)
        n_true = self.count(is_true)
        return 2 * n_true > n_leaves


@dataclass
class Maximize[T](CompTree):
    function: Callable[[T], int | float]

    def eval(self):
        domain = (eval(child) for child in self.children)
        return max(domain, key=self.function)


@dataclass
class Minimize[T](CompTree):
    function: Callable[[T], int | float]

    def eval(self):
        domain = (eval(child) for child in self.children)
        return min(domain, key=self.function)


RESULT = mp.SimpleQueue()


def nondeterministic(function):
    @ft.wraps(function)
    def wrapper(*args, **kwargs):
        if os.fork() == 0:
            result = function(*args, **kwargs)
            RESULT.put(result)
            os._exit(0)
        else:
            os.wait()
            result = RESULT.get()
            return eval(result)
    return wrapper


def guess(choices=(False, True), *, mode=Or):
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
