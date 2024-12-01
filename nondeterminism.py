from __future__ import annotations


__all__ = [
    'deterministic', 'guess', 'coguess',
    'Or', 'And', 'Count', 'Majority', 'Maximize',
    'is_leaf', 'is_true',
]


import functools as ft
import multiprocessing as mp
import os

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Callable


@dataclass
class CompTree[T](ABC):
    children: list[CompTree[T] | T]

    @abstractmethod
    def eval(self):
        ...


def is_leaf(tree):
    return not isinstance(tree, CompTree)


def eval(result):
    if is_leaf(result):
        return result
    else:
        return result.eval()
        

class Or(CompTree):
    def __bool__(self):
        return any(self.children)

    def eval(self):
        return bool(self)
            

class And(CompTree):
    def __bool__(self):
        return all(self.children)

    def eval(self):
        return bool(self)


class CountingCompTree(CompTree):
    def count(self, pred):
        cnt = pred(self)
        for child in self.children:
            if is_leaf(child):
                cnt += int(pred(child))
            else:
                cnt += child.count(pred)
        return cnt


def is_true(x):
    return x is True


class Count(CountingCompTree):
    def eval(self):
        return self.count(is_true)


class Majority(CountingCompTree):
    def eval(self):
        n_leaves = self.count(is_leaf)
        n_true = self.count(is_true)
        return 2 * n_true > n_leaves


@dataclass
class Maximize_[T](CompTree):
    function: Callable[[T], int | float]

    def eval(self):
        domain = (eval(child) for child in self.children)
        return max(domain, key=self.function)


def Maximize(function):
    def partial(children):
        return Maximize_(children, function)
    return partial


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
