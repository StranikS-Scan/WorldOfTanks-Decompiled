# Embedded file name: scripts/common/Lib/ctypes/test/test_returnfuncptrs.py
import unittest
from ctypes import *
import os
import _ctypes_test

class ReturnFuncPtrTestCase(unittest.TestCase):

    def test_with_prototype(self):
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        get_strchr.restype = CFUNCTYPE(c_char_p, c_char_p, c_char)
        strchr = get_strchr()
        self.assertEqual(strchr('abcdef', 'b'), 'bcdef')
        self.assertEqual(strchr('abcdef', 'x'), None)
        self.assertRaises(ArgumentError, strchr, 'abcdef', 3)
        self.assertRaises(TypeError, strchr, 'abcdef')
        return

    def test_without_prototype(self):
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        get_strchr.restype = c_void_p
        addr = get_strchr()
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(addr)
        self.assertTrue(strchr('abcdef', 'b'), 'bcdef')
        self.assertEqual(strchr('abcdef', 'x'), None)
        self.assertRaises(ArgumentError, strchr, 'abcdef', 3)
        self.assertRaises(TypeError, strchr, 'abcdef')
        return

    def test_from_dll(self):
        dll = CDLL(_ctypes_test.__file__)
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(('my_strchr', dll))
        self.assertTrue(strchr('abcdef', 'b'), 'bcdef')
        self.assertEqual(strchr('abcdef', 'x'), None)
        self.assertRaises(ArgumentError, strchr, 'abcdef', 3.0)
        self.assertRaises(TypeError, strchr, 'abcdef')
        return

    def test_from_dll_refcount(self):

        class BadSequence(tuple):

            def __getitem__(self, key):
                if key == 0:
                    return 'my_strchr'
                if key == 1:
                    return CDLL(_ctypes_test.__file__)
                raise IndexError

        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(BadSequence(('my_strchr', CDLL(_ctypes_test.__file__))))
        self.assertTrue(strchr('abcdef', 'b'), 'bcdef')
        self.assertEqual(strchr('abcdef', 'x'), None)
        self.assertRaises(ArgumentError, strchr, 'abcdef', 3.0)
        self.assertRaises(TypeError, strchr, 'abcdef')
        return


if __name__ == '__main__':
    unittest.main()
