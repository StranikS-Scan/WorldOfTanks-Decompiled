# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_internals.py
# Compiled at: 2010-05-25 20:46:16
import unittest
from ctypes import *
from sys import getrefcount as grc

class ObjectsTestCase(unittest.TestCase):

    def failUnlessSame(self, a, b):
        self.failUnlessEqual(id(a), id(b))

    def test_ints(self):
        i = 42000123
        self.failUnlessEqual(3, grc(i))
        ci = c_int(i)
        self.failUnlessEqual(3, grc(i))
        self.failUnlessEqual(ci._objects, None)
        return

    def test_c_char_p(self):
        s = 'Hello, World'
        self.failUnlessEqual(3, grc(s))
        cs = c_char_p(s)
        self.failUnlessEqual(4, grc(s))
        self.failUnlessSame(cs._objects, s)

    def test_simple_struct(self):

        class X(Structure):
            _fields_ = [('a', c_int), ('b', c_int)]

        a = 421234
        b = 421235
        x = X()
        self.failUnlessEqual(x._objects, None)
        x.a = a
        x.b = b
        self.failUnlessEqual(x._objects, None)
        return

    def test_embedded_structs(self):

        class X(Structure):
            _fields_ = [('a', c_int), ('b', c_int)]

        class Y(Structure):
            _fields_ = [('x', X), ('y', X)]

        y = Y()
        self.failUnlessEqual(y._objects, None)
        x1, x2 = X(), X()
        y.x, y.y = x1, x2
        self.failUnlessEqual(y._objects, {'0': {},
         '1': {}})
        x1.a, x2.b = (42, 93)
        self.failUnlessEqual(y._objects, {'0': {},
         '1': {}})
        return

    def test_xxx(self):

        class X(Structure):
            _fields_ = [('a', c_char_p), ('b', c_char_p)]

        class Y(Structure):
            _fields_ = [('x', X), ('y', X)]

        s1 = 'Hello, World'
        s2 = 'Hallo, Welt'
        x = X()
        x.a = s1
        x.b = s2
        self.failUnlessEqual(x._objects, {'0': s1,
         '1': s2})
        y = Y()
        y.x = x
        self.failUnlessEqual(y._objects, {'0': {'0': s1,
               '1': s2}})

    def test_ptr_struct(self):

        class X(Structure):
            _fields_ = [('data', POINTER(c_int))]

        A = c_int * 4
        a = A(11, 22, 33, 44)
        self.failUnlessEqual(a._objects, None)
        x = X()
        x.data = a
        return


if __name__ == '__main__':
    unittest.main()
