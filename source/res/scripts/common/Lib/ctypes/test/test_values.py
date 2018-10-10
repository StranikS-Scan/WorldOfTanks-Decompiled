# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_values.py
import unittest
from ctypes import *
import _ctypes_test

class ValuesTestCase(unittest.TestCase):

    def test_an_integer(self):
        ctdll = CDLL(_ctypes_test.__file__)
        an_integer = c_int.in_dll(ctdll, 'an_integer')
        x = an_integer.value
        self.assertEqual(x, ctdll.get_an_integer())
        an_integer.value *= 2
        self.assertEqual(x * 2, ctdll.get_an_integer())

    def test_undefined(self):
        ctdll = CDLL(_ctypes_test.__file__)
        self.assertRaises(ValueError, c_int.in_dll, ctdll, 'Undefined_Symbol')

    class Win_ValuesTestCase(unittest.TestCase):

        def test_optimizeflag(self):
            opt = c_int.in_dll(pydll, 'Py_OptimizeFlag').value
            if ValuesTestCase.__doc__ is not None:
                self.assertEqual(opt, 1)
            else:
                self.assertEqual(opt, 2)
            return

        def test_frozentable(self):

            class struct_frozen(Structure):
                _fields_ = [('name', c_char_p), ('code', POINTER(c_ubyte)), ('size', c_int)]

            FrozenTable = POINTER(struct_frozen)
            ft = FrozenTable.in_dll(pydll, 'PyImport_FrozenModules')
            items = []
            for entry in ft:
                if entry.name is None:
                    break
                items.append((entry.name, entry.size))

            import sys
            if sys.version_info[:2] >= (2, 3):
                expected = [('__hello__', 104), ('__phello__', -104), ('__phello__.spam', 104)]
            else:
                expected = [('__hello__', 100), ('__phello__', -100), ('__phello__.spam', 100)]
            self.assertEqual(items, expected)
            from ctypes import _pointer_type_cache
            del _pointer_type_cache[struct_frozen]
            return

        def test_undefined(self):
            self.assertRaises(ValueError, c_int.in_dll, pydll, 'Undefined_Symbol')


if __name__ == '__main__':
    unittest.main()
