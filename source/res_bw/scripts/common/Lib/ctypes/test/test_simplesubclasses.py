# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_simplesubclasses.py
# Compiled at: 2010-05-25 20:46:16
import unittest
from ctypes import *

class MyInt(c_int):

    def __cmp__(self, other):
        if type(other) != MyInt:
            return -1
        return cmp(self.value, other.value)

    def __hash__(self):
        return hash(self.value)


class Test(unittest.TestCase):

    def test_compare(self):
        self.failUnlessEqual(MyInt(3), MyInt(3))
        self.failIfEqual(MyInt(42), MyInt(43))

    def test_ignore_retval(self):
        proto = CFUNCTYPE(None)

        def func():
            return (1, 'abc', None)

        cb = proto(func)
        self.failUnlessEqual(None, cb())
        return

    def test_int_callback(self):
        args = []

        def func(arg):
            args.append(arg)
            return arg

        cb = CFUNCTYPE(None, MyInt)(func)
        self.failUnlessEqual(None, cb(42))
        self.failUnlessEqual(type(args[-1]), MyInt)
        cb = CFUNCTYPE(c_int, c_int)(func)
        self.failUnlessEqual(42, cb(42))
        self.failUnlessEqual(type(args[-1]), int)
        return

    def test_int_struct(self):

        class X(Structure):
            _fields_ = [('x', MyInt)]

        self.failUnlessEqual(X().x, MyInt())
        s = X()
        s.x = MyInt(42)
        self.failUnlessEqual(s.x, MyInt(42))


if __name__ == '__main__':
    unittest.main()
