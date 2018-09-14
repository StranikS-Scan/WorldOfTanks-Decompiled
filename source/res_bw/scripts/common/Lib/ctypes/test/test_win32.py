# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_win32.py
from ctypes import *
from ctypes.test import is_resource_enabled
import unittest, sys
from test import test_support as support
import _ctypes_test
if sys.platform == 'win32' and sizeof(c_void_p) == sizeof(c_int):

    class WindowsTestCase(unittest.TestCase):

        def test_callconv_1(self):
            IsWindow = windll.user32.IsWindow
            self.assertRaises(ValueError, IsWindow)
            self.assertEqual(0, IsWindow(0))
            self.assertRaises(ValueError, IsWindow, 0, 0, 0)

        def test_callconv_2(self):
            IsWindow = cdll.user32.IsWindow
            self.assertRaises(ValueError, IsWindow, None)
            return


if sys.platform == 'win32':

    class FunctionCallTestCase(unittest.TestCase):
        if is_resource_enabled('SEH'):

            def test_SEH(self):
                self.assertRaises(WindowsError, windll.kernel32.GetModuleHandleA, 32)

        def test_noargs(self):
            windll.user32.GetDesktopWindow()


    class TestWintypes(unittest.TestCase):

        def test_HWND(self):
            from ctypes import wintypes
            self.assertEqual(sizeof(wintypes.HWND), sizeof(c_void_p))

        def test_PARAM(self):
            from ctypes import wintypes
            self.assertEqual(sizeof(wintypes.WPARAM), sizeof(c_void_p))
            self.assertEqual(sizeof(wintypes.LPARAM), sizeof(c_void_p))

        def test_COMError(self):
            from _ctypes import COMError
            if support.HAVE_DOCSTRINGS:
                self.assertEqual(COMError.__doc__, 'Raised when a COM method call failed.')
            ex = COMError(-1, 'text', ('details',))
            self.assertEqual(ex.hresult, -1)
            self.assertEqual(ex.text, 'text')
            self.assertEqual(ex.details, ('details',))


class Structures(unittest.TestCase):

    def test_struct_by_value(self):

        class POINT(Structure):
            _fields_ = [('x', c_long), ('y', c_long)]

        class RECT(Structure):
            _fields_ = [('left', c_long),
             ('top', c_long),
             ('right', c_long),
             ('bottom', c_long)]

        dll = CDLL(_ctypes_test.__file__)
        pt = POINT(10, 10)
        rect = RECT(0, 0, 20, 20)
        self.assertEqual(1, dll.PointInRect(byref(rect), pt))


if __name__ == '__main__':
    unittest.main()
