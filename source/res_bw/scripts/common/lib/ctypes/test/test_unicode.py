# Embedded file name: scripts/common/Lib/ctypes/test/test_unicode.py
import unittest
import ctypes
try:
    ctypes.c_wchar
except AttributeError:
    pass
else:
    import _ctypes_test
    dll = ctypes.CDLL(_ctypes_test.__file__)
    wcslen = dll.my_wcslen
    wcslen.argtypes = [ctypes.c_wchar_p]

    class UnicodeTestCase(unittest.TestCase):

        def setUp(self):
            self.prev_conv_mode = ctypes.set_conversion_mode('ascii', 'strict')

        def tearDown(self):
            ctypes.set_conversion_mode(*self.prev_conv_mode)

        def test_ascii_strict(self):
            ctypes.set_conversion_mode('ascii', 'strict')
            self.assertEqual(wcslen(u'abc'), 3)
            self.assertEqual(wcslen(u'ab\u2070'), 3)
            self.assertEqual(wcslen('abc'), 3)
            self.assertRaises(ctypes.ArgumentError, wcslen, 'ab\xe4')

        def test_ascii_replace(self):
            ctypes.set_conversion_mode('ascii', 'replace')
            self.assertEqual(wcslen(u'abc'), 3)
            self.assertEqual(wcslen(u'ab\u2070'), 3)
            self.assertEqual(wcslen('abc'), 3)
            self.assertEqual(wcslen('ab\xe4'), 3)

        def test_ascii_ignore(self):
            ctypes.set_conversion_mode('ascii', 'ignore')
            self.assertEqual(wcslen(u'abc'), 3)
            self.assertEqual(wcslen(u'ab\u2070'), 3)
            self.assertEqual(wcslen('abc'), 3)
            self.assertEqual(wcslen('\xe4\xf6\xfc\xdf'), 0)

        def test_latin1_strict(self):
            ctypes.set_conversion_mode('latin-1', 'strict')
            self.assertEqual(wcslen(u'abc'), 3)
            self.assertEqual(wcslen(u'ab\u2070'), 3)
            self.assertEqual(wcslen('abc'), 3)
            self.assertEqual(wcslen('\xe4\xf6\xfc\xdf'), 4)

        def test_buffers(self):
            ctypes.set_conversion_mode('ascii', 'strict')
            buf = ctypes.create_unicode_buffer('abc')
            self.assertEqual(len(buf), 4)
            ctypes.set_conversion_mode('ascii', 'replace')
            buf = ctypes.create_unicode_buffer('ab\xe4\xf6\xfc')
            self.assertEqual(buf[:], u'ab\ufffd\ufffd\ufffd\x00')
            self.assertEqual(buf[::], u'ab\ufffd\ufffd\ufffd\x00')
            self.assertEqual(buf[::-1], u'\x00\ufffd\ufffd\ufffdba')
            self.assertEqual(buf[::2], u'a\ufffd\ufffd')
            self.assertEqual(buf[6:5:-1], u'')
            ctypes.set_conversion_mode('ascii', 'ignore')
            buf = ctypes.create_unicode_buffer('ab\xe4\xf6\xfc')
            self.assertEqual(buf[:], u'ab\x00\x00\x00\x00')
            self.assertEqual(buf[::], u'ab\x00\x00\x00\x00')
            self.assertEqual(buf[::-1], u'\x00\x00\x00\x00ba')
            self.assertEqual(buf[::2], u'a\x00\x00')
            self.assertEqual(buf[6:5:-1], u'')
            return


    import _ctypes_test
    func = ctypes.CDLL(_ctypes_test.__file__)._testfunc_p_p

    class StringTestCase(UnicodeTestCase):

        def setUp(self):
            self.prev_conv_mode = ctypes.set_conversion_mode('ascii', 'strict')
            func.argtypes = [ctypes.c_char_p]
            func.restype = ctypes.c_char_p

        def tearDown(self):
            ctypes.set_conversion_mode(*self.prev_conv_mode)
            func.argtypes = None
            func.restype = ctypes.c_int
            return

        def test_ascii_replace(self):
            ctypes.set_conversion_mode('ascii', 'strict')
            self.assertEqual(func('abc'), 'abc')
            self.assertEqual(func(u'abc'), 'abc')
            self.assertRaises(ctypes.ArgumentError, func, u'ab\xe4')

        def test_ascii_ignore(self):
            ctypes.set_conversion_mode('ascii', 'ignore')
            self.assertEqual(func('abc'), 'abc')
            self.assertEqual(func(u'abc'), 'abc')
            self.assertEqual(func(u'\xe4\xf6\xfc\xdf'), '')

        def test_ascii_replace(self):
            ctypes.set_conversion_mode('ascii', 'replace')
            self.assertEqual(func('abc'), 'abc')
            self.assertEqual(func(u'abc'), 'abc')
            self.assertEqual(func(u'\xe4\xf6\xfc\xdf'), '????')

        def test_buffers(self):
            ctypes.set_conversion_mode('ascii', 'strict')
            buf = ctypes.create_string_buffer(u'abc')
            self.assertEqual(len(buf), 4)
            ctypes.set_conversion_mode('ascii', 'replace')
            buf = ctypes.create_string_buffer(u'ab\xe4\xf6\xfc')
            self.assertEqual(buf[:], 'ab???\x00')
            self.assertEqual(buf[::], 'ab???\x00')
            self.assertEqual(buf[::-1], '\x00???ba')
            self.assertEqual(buf[::2], 'a??')
            self.assertEqual(buf[6:5:-1], '')
            ctypes.set_conversion_mode('ascii', 'ignore')
            buf = ctypes.create_string_buffer(u'ab\xe4\xf6\xfc')
            self.assertEqual(buf[:], 'ab\x00\x00\x00\x00')
            self.assertEqual(buf[::], 'ab\x00\x00\x00\x00')
            self.assertEqual(buf[::-1], '\x00\x00\x00\x00ba')
            return


if __name__ == '__main__':
    unittest.main()
