# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_buffers.py
# Compiled at: 2010-05-25 20:46:16
from ctypes import *
import unittest

class StringBufferTestCase(unittest.TestCase):

    def test_buffer(self):
        b = create_string_buffer(32)
        self.failUnlessEqual(len(b), 32)
        self.failUnlessEqual(sizeof(b), 32 * sizeof(c_char))
        self.failUnless(type(b[0]) is str)
        b = create_string_buffer('abc')
        self.failUnlessEqual(len(b), 4)
        self.failUnlessEqual(sizeof(b), 4 * sizeof(c_char))
        self.failUnless(type(b[0]) is str)
        self.failUnlessEqual(b[0], 'a')
        self.failUnlessEqual(b[:], 'abc\x00')
        self.failUnlessEqual(b[::], 'abc\x00')
        self.failUnlessEqual(b[::-1], '\x00cba')
        self.failUnlessEqual(b[::2], 'ac')
        self.failUnlessEqual(b[::5], 'a')
        return

    def test_string_conversion(self):
        b = create_string_buffer(u'abc')
        self.failUnlessEqual(len(b), 4)
        self.failUnlessEqual(sizeof(b), 4 * sizeof(c_char))
        self.failUnless(type(b[0]) is str)
        self.failUnlessEqual(b[0], 'a')
        self.failUnlessEqual(b[:], 'abc\x00')
        self.failUnlessEqual(b[::], 'abc\x00')
        self.failUnlessEqual(b[::-1], '\x00cba')
        self.failUnlessEqual(b[::2], 'ac')
        self.failUnlessEqual(b[::5], 'a')
        return

    try:
        c_wchar
    except NameError:
        pass
    else:

        def test_unicode_buffer(self):
            b = create_unicode_buffer(32)
            self.failUnlessEqual(len(b), 32)
            self.failUnlessEqual(sizeof(b), 32 * sizeof(c_wchar))
            self.failUnless(type(b[0]) is unicode)
            b = create_unicode_buffer(u'abc')
            self.failUnlessEqual(len(b), 4)
            self.failUnlessEqual(sizeof(b), 4 * sizeof(c_wchar))
            self.failUnless(type(b[0]) is unicode)
            self.failUnlessEqual(b[0], u'a')
            self.failUnlessEqual(b[:], 'abc\x00')
            self.failUnlessEqual(b[::], 'abc\x00')
            self.failUnlessEqual(b[::-1], '\x00cba')
            self.failUnlessEqual(b[::2], 'ac')
            self.failUnlessEqual(b[::5], 'a')
            return

        def test_unicode_conversion(self):
            b = create_unicode_buffer('abc')
            self.failUnlessEqual(len(b), 4)
            self.failUnlessEqual(sizeof(b), 4 * sizeof(c_wchar))
            self.failUnless(type(b[0]) is unicode)
            self.failUnlessEqual(b[0], u'a')
            self.failUnlessEqual(b[:], 'abc\x00')
            self.failUnlessEqual(b[::], 'abc\x00')
            self.failUnlessEqual(b[::-1], '\x00cba')
            self.failUnlessEqual(b[::2], 'ac')
            self.failUnlessEqual(b[::5], 'a')
            return


if __name__ == '__main__':
    unittest.main()
