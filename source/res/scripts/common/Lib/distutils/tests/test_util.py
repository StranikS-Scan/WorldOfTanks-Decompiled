# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_util.py
import os
import sys
import unittest
from test.test_support import run_unittest, swap_attr
from distutils.errors import DistutilsByteCompileError
from distutils.tests import support
from distutils import util
from distutils.util import byte_compile, grok_environment_error, check_environ, get_platform

class UtilTestCase(support.EnvironGuard, unittest.TestCase):

    def test_dont_write_bytecode(self):
        old_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            self.assertRaises(DistutilsByteCompileError, byte_compile, [])
        finally:
            sys.dont_write_bytecode = old_dont_write_bytecode

    def test_grok_environment_error(self):
        exc = IOError('Unable to find batch file')
        msg = grok_environment_error(exc)
        self.assertEqual(msg, 'error: Unable to find batch file')

    def test_check_environ(self):
        util._environ_checked = 0
        os.environ.pop('HOME', None)
        check_environ()
        self.assertEqual(os.environ['PLAT'], get_platform())
        self.assertEqual(util._environ_checked, 1)
        return

    @unittest.skipUnless(os.name == 'posix', 'specific to posix')
    def test_check_environ_getpwuid(self):
        util._environ_checked = 0
        os.environ.pop('HOME', None)
        import pwd

        def mock_getpwuid(uid):
            return pwd.struct_passwd((None, None, None, None, None, '/home/distutils', None))

        with swap_attr(pwd, 'getpwuid', mock_getpwuid):
            check_environ()
            self.assertEqual(os.environ['HOME'], '/home/distutils')
        util._environ_checked = 0
        os.environ.pop('HOME', None)

        def getpwuid_err(uid):
            raise KeyError

        with swap_attr(pwd, 'getpwuid', getpwuid_err):
            check_environ()
            self.assertNotIn('HOME', os.environ)
        return


def test_suite():
    return unittest.makeSuite(UtilTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
