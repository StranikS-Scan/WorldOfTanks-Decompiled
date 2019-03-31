# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_returnfuncptrs.py
# Compiled at: 2010-05-25 20:46:16
import unittest
from ctypes import *
import _ctypes_test

class ReturnFuncPtrTestCase(unittest.TestCase):

    def test_with_prototype(self):
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        get_strchr.restype = CFUNCTYPE(c_char_p, c_char_p, c_char)
        strchr = get_strchr()
        self.failUnlessEqual(strchr('abcdef', 'b'), 'bcdef')
        self.failUnlessEqual(strchr('abcdef', 'x'), None)
        self.assertRaises(ArgumentError, strchr, 'abcdef', 3)
        self.assertRaises(TypeError, strchr, 'abcdef')
        return

    def test_without_prototype(self):
        dll = CDLL(_ctypes_test.__file__)
        get_strchr = dll.get_strchr
        get_strchr.restype = c_void_p
        addr = get_strchr()
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(addr)
        self.failUnless(strchr('abcdef', 'b'), 'bcdef')
        self.failUnlessEqual(strchr('abcdef', 'x'), None)
        self.assertRaises(ArgumentError, strchr, 'abcdef', 3)
        self.assertRaises(TypeError, strchr, 'abcdef')
        return


if __name__ == '__main__':
    unittest.main()
