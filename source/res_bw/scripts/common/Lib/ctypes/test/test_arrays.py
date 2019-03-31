# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_arrays.py
# Compiled at: 2010-05-25 20:46:16
import unittest
from ctypes import *
formats = 'bBhHiIlLqQfd'
formats = (c_byte,
 c_ubyte,
 c_short,
 c_ushort,
 c_int,
 c_uint,
 c_long,
 c_ulonglong,
 c_float,
 c_double,
 c_longdouble)

class ArrayTestCase(unittest.TestCase):

    def test_simple(self):
        init = range(15, 25)
        for fmt in formats:
            alen = len(init)
            int_array = ARRAY(fmt, alen)
            ia = int_array(*init)
            self.failUnlessEqual(len(ia), alen)
            values = [ ia[i] for i in range(len(init)) ]
            self.failUnlessEqual(values, init)
            from operator import setitem
            new_values = range(42, 42 + alen)
            [ setitem(ia, n, new_values[n]) for n in range(alen) ]
            values = [ ia[i] for i in range(len(init)) ]
            self.failUnlessEqual(values, new_values)
            ia = int_array()
            values = [ ia[i] for i in range(len(init)) ]
            self.failUnlessEqual(values, [0] * len(init))
            self.assertRaises(IndexError, int_array, *range(alen * 2))

        CharArray = ARRAY(c_char, 3)
        ca = CharArray('a', 'b', 'c')
        self.assertRaises(TypeError, CharArray, 'abc')
        self.failUnlessEqual(ca[0], 'a')
        self.failUnlessEqual(ca[1], 'b')
        self.failUnlessEqual(ca[2], 'c')
        self.failUnlessEqual(ca[-3], 'a')
        self.failUnlessEqual(ca[-2], 'b')
        self.failUnlessEqual(ca[-1], 'c')
        self.failUnlessEqual(len(ca), 3)
        from operator import getslice, delitem
        self.assertRaises(TypeError, getslice, ca, 0, 1, -1)
        self.assertRaises(TypeError, delitem, ca, 0)

    def test_numeric_arrays(self):
        alen = 5
        numarray = ARRAY(c_int, alen)
        na = numarray()
        values = [ na[i] for i in range(alen) ]
        self.failUnlessEqual(values, [0] * alen)
        na = numarray(*([c_int()] * alen))
        values = [ na[i] for i in range(alen) ]
        self.failUnlessEqual(values, [0] * alen)
        na = numarray(1, 2, 3, 4, 5)
        values = [ i for i in na ]
        self.failUnlessEqual(values, [1,
         2,
         3,
         4,
         5])
        na = numarray(*map(c_int, (1, 2, 3, 4, 5)))
        values = [ i for i in na ]
        self.failUnlessEqual(values, [1,
         2,
         3,
         4,
         5])

    def test_classcache(self):
        self.failUnless(ARRAY(c_int, 3) is not ARRAY(c_int, 4))
        self.failUnless(ARRAY(c_int, 3) is ARRAY(c_int, 3))

    def test_from_address(self):
        p = create_string_buffer('foo')
        sz = (c_char * 3).from_address(addressof(p))
        self.failUnlessEqual(sz[:], 'foo')
        self.failUnlessEqual(sz[::], 'foo')
        self.failUnlessEqual(sz[::-1], 'oof')
        self.failUnlessEqual(sz[::3], 'f')
        self.failUnlessEqual(sz[1:4:2], 'o')
        self.failUnlessEqual(sz.value, 'foo')
        return

    try:
        create_unicode_buffer
    except NameError:
        pass
    else:

        def test_from_addressW(self):
            p = create_unicode_buffer('foo')
            sz = (c_wchar * 3).from_address(addressof(p))
            self.failUnlessEqual(sz[:], 'foo')
            self.failUnlessEqual(sz[::], 'foo')
            self.failUnlessEqual(sz[::-1], 'oof')
            self.failUnlessEqual(sz[::3], 'f')
            self.failUnlessEqual(sz[1:4:2], 'o')
            self.failUnlessEqual(sz.value, 'foo')
            return

    def test_cache(self):

        class my_int(c_int):
            pass

        t1 = my_int * 1
        t2 = my_int * 1
        self.failUnless(t1 is t2)


if __name__ == '__main__':
    unittest.main()
