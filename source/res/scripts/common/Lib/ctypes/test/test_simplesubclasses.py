# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_simplesubclasses.py
import unittest
from ctypes import *

class MyInt(c_int):

    def __cmp__(self, other):
        return -1 if type(other) != MyInt else cmp(self.value, other.value)

    def __hash__(self):
        return hash(self.value)


class Test(unittest.TestCase):

    def test_compare(self):
        self.assertEqual(MyInt(3), MyInt(3))
        self.assertNotEqual(MyInt(42), MyInt(43))

    def test_ignore_retval(self):
        proto = CFUNCTYPE(None)

        def func():
            return (1, 'abc', None)

        cb = proto(func)
        self.assertEqual(None, cb())
        return

    def test_int_callback(self):
        args = []

        def func(arg):
            args.append(arg)
            return arg

        cb = CFUNCTYPE(None, MyInt)(func)
        self.assertEqual(None, cb(42))
        self.assertEqual(type(args[-1]), MyInt)
        cb = CFUNCTYPE(c_int, c_int)(func)
        self.assertEqual(42, cb(42))
        self.assertEqual(type(args[-1]), int)
        return

    def test_int_struct(self):

        class X(Structure):
            _fields_ = [('x', MyInt)]

        self.assertEqual(X().x, MyInt())
        s = X()
        s.x = MyInt(42)
        self.assertEqual(s.x, MyInt(42))


if __name__ == '__main__':
    unittest.main()
