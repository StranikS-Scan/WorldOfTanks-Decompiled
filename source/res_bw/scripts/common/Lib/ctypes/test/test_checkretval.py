# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ctypes/test/test_checkretval.py
# Compiled at: 2010-05-25 20:46:16
import unittest
from ctypes import *

class CHECKED(c_int):

    def _check_retval_(value):
        return str(value.value)

    _check_retval_ = staticmethod(_check_retval_)


class Test(unittest.TestCase):

    def test_checkretval(self):
        import _ctypes_test
        dll = CDLL(_ctypes_test.__file__)
        self.failUnlessEqual(42, dll._testfunc_p_p(42))
        dll._testfunc_p_p.restype = CHECKED
        self.failUnlessEqual('42', dll._testfunc_p_p(42))
        dll._testfunc_p_p.restype = None
        self.failUnlessEqual(None, dll._testfunc_p_p(42))
        del dll._testfunc_p_p.restype
        self.failUnlessEqual(42, dll._testfunc_p_p(42))
        return

    try:
        oledll
    except NameError:
        pass
    else:

        def test_oledll(self):
            self.failUnlessRaises(WindowsError, oledll.oleaut32.CreateTypeLib2, 0, None, None)
            return


if __name__ == '__main__':
    unittest.main()
