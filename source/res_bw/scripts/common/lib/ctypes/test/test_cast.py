# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_cast.py
from ctypes import *
import unittest
import sys

class Test(unittest.TestCase):

    def test_array2pointer(self):
        array = (c_int * 3)(42, 17, 2)
        ptr = cast(array, POINTER(c_int))
        self.assertEqual([ ptr[i] for i in range(3) ], [42, 17, 2])
        if 2 * sizeof(c_short) == sizeof(c_int):
            ptr = cast(array, POINTER(c_short))
            if sys.byteorder == 'little':
                self.assertEqual([ ptr[i] for i in range(6) ], [42,
                 0,
                 17,
                 0,
                 2,
                 0])
            else:
                self.assertEqual([ ptr[i] for i in range(6) ], [0,
                 42,
                 0,
                 17,
                 0,
                 2])

    def test_address2pointer(self):
        array = (c_int * 3)(42, 17, 2)
        address = addressof(array)
        ptr = cast(c_void_p(address), POINTER(c_int))
        self.assertEqual([ ptr[i] for i in range(3) ], [42, 17, 2])
        ptr = cast(address, POINTER(c_int))
        self.assertEqual([ ptr[i] for i in range(3) ], [42, 17, 2])

    def test_p2a_objects(self):
        array = (c_char_p * 5)()
        self.assertEqual(array._objects, None)
        array[0] = 'foo bar'
        self.assertEqual(array._objects, {'0': 'foo bar'})
        p = cast(array, POINTER(c_char_p))
        self.assertIs(p._objects, array._objects)
        self.assertEqual(array._objects, {'0': 'foo bar',
         id(array): array})
        p[0] = 'spam spam'
        self.assertEqual(p._objects, {'0': 'spam spam',
         id(array): array})
        self.assertIs(array._objects, p._objects)
        p[1] = 'foo bar'
        self.assertEqual(p._objects, {'1': 'foo bar',
         '0': 'spam spam',
         id(array): array})
        self.assertIs(array._objects, p._objects)
        return

    def test_other(self):
        p = cast((c_int * 4)(1, 2, 3, 4), POINTER(c_int))
        self.assertEqual(p[:4], [1,
         2,
         3,
         4])
        self.assertEqual(p[:4:], [1,
         2,
         3,
         4])
        self.assertEqual(p[3:-1:-1], [4,
         3,
         2,
         1])
        self.assertEqual(p[:4:3], [1, 4])
        c_int()
        self.assertEqual(p[:4], [1,
         2,
         3,
         4])
        self.assertEqual(p[:4:], [1,
         2,
         3,
         4])
        self.assertEqual(p[3:-1:-1], [4,
         3,
         2,
         1])
        self.assertEqual(p[:4:3], [1, 4])
        p[2] = 96
        self.assertEqual(p[:4], [1,
         2,
         96,
         4])
        self.assertEqual(p[:4:], [1,
         2,
         96,
         4])
        self.assertEqual(p[3:-1:-1], [4,
         96,
         2,
         1])
        self.assertEqual(p[:4:3], [1, 4])
        c_int()
        self.assertEqual(p[:4], [1,
         2,
         96,
         4])
        self.assertEqual(p[:4:], [1,
         2,
         96,
         4])
        self.assertEqual(p[3:-1:-1], [4,
         96,
         2,
         1])
        self.assertEqual(p[:4:3], [1, 4])
        return

    def test_char_p(self):
        s = c_char_p('hiho')
        self.assertEqual(cast(cast(s, c_void_p), c_char_p).value, 'hiho')

    try:
        c_wchar_p
    except NameError:
        pass
    else:

        def test_wchar_p(self):
            s = c_wchar_p('hiho')
            self.assertEqual(cast(cast(s, c_void_p), c_wchar_p).value, 'hiho')


if __name__ == '__main__':
    unittest.main()
