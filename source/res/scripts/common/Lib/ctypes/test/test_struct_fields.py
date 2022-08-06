# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_struct_fields.py
import unittest
from ctypes import *

class StructFieldsTestCase(unittest.TestCase):

    def test_1_A(self):

        class X(Structure):
            pass

        self.assertEqual(sizeof(X), 0)
        X._fields_ = []
        self.assertRaises(AttributeError, setattr, X, '_fields_', [])

    def test_1_B(self):

        class X(Structure):
            _fields_ = []

        self.assertRaises(AttributeError, setattr, X, '_fields_', [])

    def test_2(self):

        class X(Structure):
            pass

        X()
        self.assertRaises(AttributeError, setattr, X, '_fields_', [])

    def test_3(self):

        class X(Structure):
            pass

        class Y(Structure):
            _fields_ = [('x', X)]

        self.assertRaises(AttributeError, setattr, X, '_fields_', [])

    def test_4(self):

        class X(Structure):
            pass

        class Y(X):
            pass

        self.assertRaises(AttributeError, setattr, X, '_fields_', [])
        Y._fields_ = []
        self.assertRaises(AttributeError, setattr, X, '_fields_', [])

    def test___set__(self):

        class MyCStruct(Structure):
            _fields_ = (('field', c_int),)

        self.assertRaises(TypeError, MyCStruct.field.__set__, 'wrong type self', 42)

        class MyCUnion(Union):
            _fields_ = (('field', c_int),)

        self.assertRaises(TypeError, MyCUnion.field.__set__, 'wrong type self', 42)

    def test___get__(self):

        class MyCStruct(Structure):
            _fields_ = (('field', c_int),)

        self.assertRaises(TypeError, MyCStruct.field.__get__, 'wrong type self', 42)

        class MyCUnion(Union):
            _fields_ = (('field', c_int),)

        self.assertRaises(TypeError, MyCUnion.field.__get__, 'wrong type self', 42)


if __name__ == '__main__':
    unittest.main()
