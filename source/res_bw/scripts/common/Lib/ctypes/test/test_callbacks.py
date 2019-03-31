# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_callbacks.py
# Compiled at: 2010-05-25 20:46:16
import unittest
from ctypes import *
import _ctypes_test

class Callbacks(unittest.TestCase):
    functype = CFUNCTYPE

    def callback(self, *args):
        self.got_args = args
        return args[-1]

    def check_type(self, typ, arg):
        PROTO = self.functype.im_func(typ, typ)
        result = PROTO(self.callback)(arg)
        if typ == c_float:
            self.failUnlessAlmostEqual(result, arg, places=5)
        else:
            self.failUnlessEqual(self.got_args, (arg,))
            self.failUnlessEqual(result, arg)
        PROTO = self.functype.im_func(typ, c_byte, typ)
        result = PROTO(self.callback)(-3, arg)
        if typ == c_float:
            self.failUnlessAlmostEqual(result, arg, places=5)
        else:
            self.failUnlessEqual(self.got_args, (-3, arg))
            self.failUnlessEqual(result, arg)

    def test_byte(self):
        self.check_type(c_byte, 42)
        self.check_type(c_byte, -42)

    def test_ubyte(self):
        self.check_type(c_ubyte, 42)

    def test_short(self):
        self.check_type(c_short, 42)
        self.check_type(c_short, -42)

    def test_ushort(self):
        self.check_type(c_ushort, 42)

    def test_int(self):
        self.check_type(c_int, 42)
        self.check_type(c_int, -42)

    def test_uint(self):
        self.check_type(c_uint, 42)

    def test_long(self):
        self.check_type(c_long, 42)
        self.check_type(c_long, -42)

    def test_ulong(self):
        self.check_type(c_ulong, 42)

    def test_longlong(self):
        self.check_type(c_longlong, 42)
        self.check_type(c_longlong, -42)

    def test_ulonglong(self):
        self.check_type(c_ulonglong, 42)

    def test_float(self):
        import math
        self.check_type(c_float, math.e)
        self.check_type(c_float, -math.e)

    def test_double(self):
        self.check_type(c_double, 3.14)
        self.check_type(c_double, -3.14)

    def test_longdouble(self):
        self.check_type(c_longdouble, 3.14)
        self.check_type(c_longdouble, -3.14)

    def test_char(self):
        self.check_type(c_char, 'x')
        self.check_type(c_char, 'a')

    def test_pyobject(self):
        o = ()
        from sys import getrefcount as grc
        for o in ((), [], object()):
            initial = grc(o)
            self.check_type(py_object, o)
            before = grc(o)
            self.check_type(py_object, o)
            after = grc(o)
            self.failUnlessEqual((after, o), (before, o))

    def test_unsupported_restype_1(self):
        prototype = self.functype.im_func(POINTER(c_double))
        self.assertRaises(TypeError, prototype, lambda : None)

    def test_unsupported_restype_2(self):
        prototype = self.functype.im_func(object)
        self.assertRaises(TypeError, prototype, lambda : None)


try:
    WINFUNCTYPE
except NameError:
    pass
else:

    class StdcallCallbacks(Callbacks):
        functype = WINFUNCTYPE


class SampleCallbacksTestCase(unittest.TestCase):

    def test_integrate(self):
        dll = CDLL(_ctypes_test.__file__)
        CALLBACK = CFUNCTYPE(c_double, c_double)
        integrate = dll.integrate
        integrate.argtypes = (c_double,
         c_double,
         CALLBACK,
         c_long)
        integrate.restype = c_double

        def func(x):
            return x ** 2

        result = integrate(0.0, 1.0, CALLBACK(func), 10)
        diff = abs(result - 1.0 / 3.0)
        self.failUnless(diff < 0.01, '%s not less than 0.01' % diff)


if __name__ == '__main__':
    unittest.main()
