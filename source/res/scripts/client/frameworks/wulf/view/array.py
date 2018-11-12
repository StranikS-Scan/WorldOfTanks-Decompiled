# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/array.py
import GUI
from ..py_object_binder import PyObjectEntity

class Array(PyObjectEntity):
    __slots__ = ()

    def __init__(self):
        super(Array, self).__init__(GUI.PyObjectArray())

    def __len__(self):
        return self.proxy.getSize()

    def __getitem__(self, index):
        return self.proxy.getValue(index)

    def __iter__(self):
        for index in xrange(0, self.proxy.getSize()):
            yield self.proxy.getValue(index)

    def clear(self):
        self.proxy.clear()

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

    def setArray(self, index, value):
        self.proxy.setArray(index, value.proxy)

    def remove(self, index):
        self.proxy.removeValue(index)

    def removeValues(self, indexes):
        self.proxy.removeValues(indexes)

    def invalidate(self):
        self.proxy.invalidate()
