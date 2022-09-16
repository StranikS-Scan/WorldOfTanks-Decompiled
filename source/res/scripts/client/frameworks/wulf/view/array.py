# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/array.py
import typing
from contextlib import contextmanager
from typing import Union
from ..py_object_binder import PyObjectEntity
from ..py_object_wrappers import PyObjectArray
T = typing.TypeVar('T')

class Array(PyObjectEntity, typing.Iterable[T]):
    __slots__ = ()

    def __init__(self):
        super(Array, self).__init__(PyObjectArray())

    def __repr__(self):
        return 'Array(size={})'.format(self.proxy.getSize() if self.proxy is not None else 0)

    def __str__(self):
        return self.proxy.toString()

    def __len__(self):
        return self.proxy.getSize()

    def __getitem__(self, index):
        return (self.proxy.getValue(i) for i in xrange(index.start or 0, index.stop or len(self), index.step or 1)) if isinstance(index, slice) else self.proxy.getValue(index)

    def __iter__(self):
        for index in xrange(0, self.proxy.getSize()):
            yield self.proxy.getValue(index)

    def reserve(self, capacity):
        self.proxy.reserve(capacity)

    def clear(self):
        self.proxy.clear()

    def getValue(self, index):
        return self.proxy.getValue(index)

    def addNumber(self, value):
        self.proxy.addNumber(value)

    def addReal(self, value):
        self.proxy.addReal(value)

    def addBool(self, value):
        self.proxy.addBool(value)

    def addString(self, value):
        self.proxy.addString(value)

    def addViewModel(self, value):
        self.proxy.addViewModel(value.proxy)

    def addResource(self, value):
        self.proxy.addResource(value)

    def addArray(self, value):
        self.proxy.addArray(value.proxy)

    def setNumber(self, index, value):
        self.proxy.setNumber(index, value)

    def setReal(self, index, value):
        self.proxy.setReal(index, value)

    def setBool(self, index, value):
        self.proxy.setBool(index, value)

    def setString(self, index, value):
        self.proxy.setString(index, value)

    def setViewModel(self, index, value):
        self.proxy.setViewModel(index, value.proxy)

    def setResource(self, index, value):
        self.proxy.setResource(index, value)

    def setArray(self, index, value):
        self.proxy.setArray(index, value.proxy)

    def remove(self, index):
        self.proxy.removeValue(index)

    def removeValues(self, indexes):
        self.proxy.removeValues(indexes)

    def invalidate(self):
        self.proxy.invalidate()

    @contextmanager
    def transaction(self):
        yield self
        self.invalidate()


def fillIntsArray(numbers, array):
    array.clear()
    for n in numbers:
        array.addNumber(n)

    array.invalidate()


def fillFloatsArray(floats, array):
    array.clear()
    for f in floats:
        array.addReal(f)

    array.invalidate()


def fillBoolsArray(bools, array):
    array.clear()
    for b in bools:
        array.addBool(b)

    array.invalidate()


def fillStringsArray(strings, array):
    array.clear()
    for s in strings:
        array.addString(s)

    array.invalidate()


def fillViewModelsArray(viewModels, array):
    array.clear()
    for vm in viewModels:
        array.addViewModel(vm)

    array.invalidate()


def fillResourcesArray(resources, array):
    array.clear()
    for r in resources:
        array.addResource(r)

    array.invalidate()


def fillArraysArray(arrays, array):
    array.clear()
    for a in arrays:
        array.addArray(a)

    array.invalidate()
