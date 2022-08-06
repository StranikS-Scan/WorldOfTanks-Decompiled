# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_wintypes.py
import sys
import unittest
from ctypes import *

@unittest.skipUnless(sys.platform.startswith('win'), 'Windows-only test')
class WinTypesTest(unittest.TestCase):

    def test_variant_bool(self):
        from ctypes import wintypes
        for true_value in (1, 32767, 32768, 65535, 65537):
            true = POINTER(c_int16)(c_int16(true_value))
            value = cast(true, POINTER(wintypes.VARIANT_BOOL))
            self.assertEqual(repr(value.contents), 'VARIANT_BOOL(True)')
            vb = wintypes.VARIANT_BOOL()
            self.assertIs(vb.value, False)
            vb.value = True
            self.assertIs(vb.value, True)
            vb.value = true_value
            self.assertIs(vb.value, True)

        for false_value in (0,
         65536,
         262144,
         8589934592L):
            false = POINTER(c_int16)(c_int16(false_value))
            value = cast(false, POINTER(wintypes.VARIANT_BOOL))
            self.assertEqual(repr(value.contents), 'VARIANT_BOOL(False)')

        for set_value in (65536, 262144, 8589934592L):
            vb = wintypes.VARIANT_BOOL()
            vb.value = set_value
            self.assertIs(vb.value, True)

        vb = wintypes.VARIANT_BOOL()
        vb.value = [2, 3]
        self.assertIs(vb.value, True)
        vb.value = []
        self.assertIs(vb.value, False)


if __name__ == '__main__':
    unittest.main()
