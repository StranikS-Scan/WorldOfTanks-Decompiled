# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_strings.py
import unittest
from ctypes import *
from test import test_support

class StringArrayTestCase(unittest.TestCase):

    def test(self):
        BUF = c_char * 4
        buf = BUF('a', 'b', 'c')
        self.assertEqual(buf.value, 'abc')
        self.assertEqual(buf.raw, 'abc\x00')
        buf.value = 'ABCD'
        self.assertEqual(buf.value, 'ABCD')
        self.assertEqual(buf.raw, 'ABCD')
        buf.value = 'x'
        self.assertEqual(buf.value, 'x')
        self.assertEqual(buf.raw, 'x\x00CD')
        buf[1] = 'Z'
        self.assertEqual(buf.value, 'xZCD')
        self.assertEqual(buf.raw, 'xZCD')
        self.assertRaises(ValueError, setattr, buf, 'value', 'aaaaaaaa')
        self.assertRaises(TypeError, setattr, buf, 'value', 42)

    def test_c_buffer_value(self, memoryview=memoryview):
        buf = c_buffer(32)
        buf.value = 'Hello, World'
        self.assertEqual(buf.value, 'Hello, World')
        self.assertRaises(TypeError, setattr, buf, 'value', memoryview('Hello, World'))
        self.assertRaises(TypeError, setattr, buf, 'value', memoryview('abc'))
        self.assertRaises(ValueError, setattr, buf, 'raw', memoryview('x' * 100))

    def test_c_buffer_raw(self, memoryview=memoryview):
        buf = c_buffer(32)
        buf.raw = memoryview('Hello, World')
        self.assertEqual(buf.value, 'Hello, World')
        self.assertRaises(TypeError, setattr, buf, 'value', memoryview('abc'))
        self.assertRaises(ValueError, setattr, buf, 'raw', memoryview('x' * 100))

    def test_c_buffer_deprecated(self):
        with test_support.check_py3k_warnings():
            self.test_c_buffer_value(buffer)
            self.test_c_buffer_raw(buffer)

    def test_param_1(self):
        BUF = c_char * 4
        buf = BUF()

    def test_param_2(self):
        BUF = c_char * 4
        buf = BUF()


try:
    c_wchar
except NameError:
    pass
else:

    class WStringArrayTestCase(unittest.TestCase):

        def test(self):
            BUF = c_wchar * 4
            buf = BUF(u'a', u'b', u'c')
            self.assertEqual(buf.value, u'abc')
            buf.value = u'ABCD'
            self.assertEqual(buf.value, u'ABCD')
            buf.value = u'x'
            self.assertEqual(buf.value, u'x')
            buf[1] = u'Z'
            self.assertEqual(buf.value, u'xZCD')


class StringTestCase(unittest.TestCase):

    def XX_test_basic_strings(self):
        cs = c_string('abcdef')
        self.assertRaises(TypeError, len, cs)
        self.assertEqual(sizeof(cs), 7)
        self.assertEqual(cs.value, 'abcdef')
        self.assertEqual(c_string('abc\x00def').value, 'abc')
        self.assertEqual(cs.raw, 'abcdef\x00')
        self.assertEqual(c_string('abc\x00def').raw, 'abc\x00def\x00')
        cs.value = 'ab'
        self.assertEqual(cs.value, 'ab')
        self.assertEqual(cs.raw, 'ab\x00\x00\x00\x00\x00')
        cs.raw = 'XY'
        self.assertEqual(cs.value, 'XY')
        self.assertEqual(cs.raw, 'XY\x00\x00\x00\x00\x00')
        self.assertRaises(TypeError, c_string, u'123')

    def XX_test_sized_strings(self):
        self.assertRaises(TypeError, c_string, None)
        self.assertEqual(len(c_string(32).raw), 32)
        self.assertRaises(ValueError, c_string, -1)
        self.assertRaises(ValueError, c_string, 0)
        self.assertEqual(c_string(2).raw[-1], '\x00')
        self.assertEqual(len(c_string(2).raw), 2)
        return

    def XX_test_initialized_strings(self):
        self.assertEqual(c_string('ab', 4).raw[:2], 'ab')
        self.assertEqual(c_string('ab', 4).raw[:2:], 'ab')
        self.assertEqual(c_string('ab', 4).raw[:2:-1], 'ba')
        self.assertEqual(c_string('ab', 4).raw[:2:2], 'a')
        self.assertEqual(c_string('ab', 4).raw[-1], '\x00')
        self.assertEqual(c_string('ab', 2).raw, 'a\x00')
        return

    def XX_test_toolong(self):
        cs = c_string('abcdef')
        self.assertRaises(ValueError, setattr, cs, 'value', '123456789012345')
        self.assertRaises(ValueError, setattr, cs, 'value', '1234567')


try:
    c_wchar
except NameError:
    pass
else:

    class WStringTestCase(unittest.TestCase):

        def test_wchar(self):
            c_wchar(u'x')
            repr(byref(c_wchar(u'x')))
            c_wchar('x')

        def X_test_basic_wstrings(self):
            cs = c_wstring(u'abcdef')
            self.assertEqual(sizeof(cs), 14)
            self.assertEqual(cs.value, u'abcdef')
            self.assertEqual(c_wstring(u'abc\x00def').value, u'abc')
            self.assertEqual(c_wstring(u'abc\x00def').value, u'abc')
            self.assertEqual(cs.raw, u'abcdef\x00')
            self.assertEqual(c_wstring(u'abc\x00def').raw, u'abc\x00def\x00')
            cs.value = u'ab'
            self.assertEqual(cs.value, u'ab')
            self.assertEqual(cs.raw, u'ab\x00\x00\x00\x00\x00')
            self.assertRaises(TypeError, c_wstring, '123')
            self.assertRaises(ValueError, c_wstring, 0)

        def X_test_toolong(self):
            cs = c_wstring(u'abcdef')
            self.assertRaises(ValueError, setattr, cs, 'value', u'123456789012345')
            self.assertRaises(ValueError, setattr, cs, 'value', u'1234567')


def run_test(rep, msg, func, arg):
    items = range(rep)
    from time import clock
    start = clock()
    for i in items:
        func(arg)
        func(arg)
        func(arg)
        func(arg)
        func(arg)

    stop = clock()
    print '%20s: %.2f us' % (msg, (stop - start) * 1000000.0 / 5 / rep)


def check_perf():
    REP = 200000
    run_test(REP, 'c_string(None)', c_string, None)
    run_test(REP, "c_string('abc')", c_string, 'abc')
    return


if __name__ == '__main__':
    unittest.main()
