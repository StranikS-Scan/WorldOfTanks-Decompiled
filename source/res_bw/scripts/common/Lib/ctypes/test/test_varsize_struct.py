# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_varsize_struct.py
# Compiled at: 2010-05-25 20:46:16
from ctypes import *
import unittest

class VarSizeTest(unittest.TestCase):

    def test_resize(self):

        class X(Structure):
            _fields_ = [('item', c_int), ('array', c_int * 1)]

        self.failUnlessEqual(sizeof(X), sizeof(c_int) * 2)
        x = X()
        x.item = 42
        x.array[0] = 100
        self.failUnlessEqual(sizeof(x), sizeof(c_int) * 2)
        new_size = sizeof(X) + sizeof(c_int) * 1
        resize(x, new_size)
        self.failUnlessEqual(sizeof(x), new_size)
        self.failUnlessEqual((x.item, x.array[0]), (42, 100))
        new_size = sizeof(X) + sizeof(c_int) * 9
        resize(x, new_size)
        self.failUnlessEqual(sizeof(x), new_size)
        self.failUnlessEqual((x.item, x.array[0]), (42, 100))
        new_size = sizeof(X) + sizeof(c_int) * 1
        resize(x, new_size)
        self.failUnlessEqual(sizeof(x), new_size)
        self.failUnlessEqual((x.item, x.array[0]), (42, 100))

    def test_array_invalid_length(self):
        self.failUnlessRaises(ValueError, lambda : c_int * -1)
        self.failUnlessRaises(ValueError, lambda : c_int * -3)

    def test_zerosized_array(self):
        array = (c_int * 0)()
        self.failUnlessRaises(IndexError, array.__setitem__, 0, None)
        self.failUnlessRaises(IndexError, array.__getitem__, 0)
        self.failUnlessRaises(IndexError, array.__setitem__, 1, None)
        self.failUnlessRaises(IndexError, array.__getitem__, 1)
        self.failUnlessRaises(IndexError, array.__setitem__, -1, None)
        self.failUnlessRaises(IndexError, array.__getitem__, -1)
        return


if __name__ == '__main__':
    unittest.main()
