# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_numbers.py
from ctypes import *
import unittest
import struct

def valid_ranges(*types):
    result = []
    for t in types:
        fmt = t._type_
        size = struct.calcsize(fmt)
        a = struct.unpack(fmt, ('\x00' * 32)[:size])[0]
        b = struct.unpack(fmt, ('\xff' * 32)[:size])[0]
        c = struct.unpack(fmt, ('\x7f' + '\x00' * 32)[:size])[0]
        d = struct.unpack(fmt, ('\x80' + '\xff' * 32)[:size])[0]
        result.append((min(a, b, c, d), max(a, b, c, d)))

    return result


ArgType = type(byref(c_int(0)))
unsigned_types = [c_ubyte,
 c_ushort,
 c_uint,
 c_ulong]
signed_types = [c_byte,
 c_short,
 c_int,
 c_long,
 c_longlong]
bool_types = []
float_types = [c_double, c_float]
try:
    c_ulonglong
    c_longlong
except NameError:
    pass
else:
    unsigned_types.append(c_ulonglong)
    signed_types.append(c_longlong)

try:
    c_bool
except NameError:
    pass
else:
    bool_types.append(c_bool)

unsigned_ranges = valid_ranges(*unsigned_types)
signed_ranges = valid_ranges(*signed_types)
bool_values = [True,
 False,
 0,
 1,
 -1,
 5000,
 'test',
 [],
 [1]]

class NumberTestCase(unittest.TestCase):

    def test_default_init(self):
        for t in signed_types + unsigned_types + float_types:
            self.assertEqual(t().value, 0)

    def test_unsigned_values(self):
        for t, (l, h) in zip(unsigned_types, unsigned_ranges):
            self.assertEqual(t(l).value, l)
            self.assertEqual(t(h).value, h)

    def test_signed_values(self):
        for t, (l, h) in zip(signed_types, signed_ranges):
            self.assertEqual(t(l).value, l)
            self.assertEqual(t(h).value, h)

    def test_bool_values(self):
        from operator import truth
        for t, v in zip(bool_types, bool_values):
            self.assertEqual(t(v).value, truth(v))

    def test_typeerror(self):
        for t in signed_types + unsigned_types + float_types:
            self.assertRaises(TypeError, t, '')
            self.assertRaises(TypeError, t, None)

        return

    def test_from_param(self):
        for t in signed_types + unsigned_types + float_types:
            self.assertEqual(ArgType, type(t.from_param(0)))

    def test_byref(self):
        for t in signed_types + unsigned_types + float_types + bool_types:
            parm = byref(t())
            self.assertEqual(ArgType, type(parm))

    def test_floats(self):

        class FloatLike(object):

            def __float__(self):
                pass

        f = FloatLike()
        for t in float_types:
            self.assertEqual(t(2.0).value, 2.0)
            self.assertEqual(t(2).value, 2.0)
            self.assertEqual(t(2L).value, 2.0)
            self.assertEqual(t(f).value, 2.0)

    def test_integers(self):

        class FloatLike(object):

            def __float__(self):
                pass

        f = FloatLike()

        class IntLike(object):

            def __int__(self):
                pass

        i = IntLike()
        for t in signed_types + unsigned_types:
            self.assertRaises(TypeError, t, 3.14)
            self.assertRaises(TypeError, t, f)
            self.assertEqual(t(i).value, 2)

    def test_sizes(self):
        for t in signed_types + unsigned_types + float_types + bool_types:
            try:
                size = struct.calcsize(t._type_)
            except struct.error:
                continue

            self.assertEqual(sizeof(t), size)
            self.assertEqual(sizeof(t()), size)

    def test_alignments(self):
        for t in signed_types + unsigned_types + float_types:
            code = t._type_
            align = struct.calcsize('c%c' % code) - struct.calcsize(code)
            self.assertEqual((code, alignment(t)), (code, align))
            self.assertEqual((code, alignment(t())), (code, align))

    def test_int_from_address(self):
        from array import array
        for t in signed_types + unsigned_types:
            try:
                array(t._type_)
            except ValueError:
                continue

            a = array(t._type_, [100])
            v = t.from_address(a.buffer_info()[0])
            self.assertEqual(v.value, a[0])
            self.assertEqual(type(v), t)
            a[0] = 42
            self.assertEqual(v.value, a[0])

    def test_float_from_address(self):
        from array import array
        for t in float_types:
            a = array(t._type_, [3.14])
            v = t.from_address(a.buffer_info()[0])
            self.assertEqual(v.value, a[0])
            self.assertIs(type(v), t)
            a[0] = 2.3456e+17
            self.assertEqual(v.value, a[0])
            self.assertIs(type(v), t)

    def test_char_from_address(self):
        from ctypes import c_char
        from array import array
        a = array('c', 'x')
        v = c_char.from_address(a.buffer_info()[0])
        self.assertEqual(v.value, a[0])
        self.assertIs(type(v), c_char)
        a[0] = '?'
        self.assertEqual(v.value, a[0])

    def test_init(self):
        self.assertRaises(TypeError, c_int, c_long(42))

    def test_float_overflow(self):
        import sys
        big_int = int(sys.float_info.max) * 2
        for t in float_types + [c_longdouble]:
            self.assertRaises(OverflowError, t, big_int)
            if hasattr(t, '__ctype_be__'):
                self.assertRaises(OverflowError, t.__ctype_be__, big_int)
            if hasattr(t, '__ctype_le__'):
                self.assertRaises(OverflowError, t.__ctype_le__, big_int)


from ctypes import _SimpleCData

class c_int_S(_SimpleCData):
    _type_ = 'i'
    __slots__ = []


def run_test(rep, msg, func, arg=None):
    items = range(rep)
    from time import clock
    if arg is not None:
        start = clock()
        for i in items:
            func(arg)
            func(arg)
            func(arg)
            func(arg)
            func(arg)

        stop = clock()
    else:
        start = clock()
        for i in items:
            func()
            func()
            func()
            func()
            func()

        stop = clock()
    print '%15s: %.2f us' % (msg, (stop - start) * 1000000.0 / 5 / rep)
    return


def check_perf():
    from ctypes import c_int
    REP = 200000
    run_test(REP, 'int()', int)
    run_test(REP, 'int(999)', int)
    run_test(REP, 'c_int()', c_int)
    run_test(REP, 'c_int(999)', c_int)
    run_test(REP, 'c_int_S()', c_int_S)
    run_test(REP, 'c_int_S(999)', c_int_S)


if __name__ == '__main__':
    unittest.main()
