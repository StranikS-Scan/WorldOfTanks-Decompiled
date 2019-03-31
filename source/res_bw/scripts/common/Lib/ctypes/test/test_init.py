# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_init.py
# Compiled at: 2010-05-25 20:46:16
from ctypes import *
import unittest

class X(Structure):
    _fields_ = [('a', c_int), ('b', c_int)]
    new_was_called = False

    def __new__(cls):
        result = super(X, cls).__new__(cls)
        result.new_was_called = True
        return result

    def __init__(self):
        self.a = 9
        self.b = 12


class Y(Structure):
    _fields_ = [('x', X)]


class InitTest(unittest.TestCase):

    def test_get(self):
        y = Y()
        self.failUnlessEqual((y.x.a, y.x.b), (0, 0))
        self.failUnlessEqual(y.x.new_was_called, False)
        x = X()
        self.failUnlessEqual((x.a, x.b), (9, 12))
        self.failUnlessEqual(x.new_was_called, True)
        y.x = x
        self.failUnlessEqual((y.x.a, y.x.b), (9, 12))
        self.failUnlessEqual(y.x.new_was_called, False)


if __name__ == '__main__':
    unittest.main()
