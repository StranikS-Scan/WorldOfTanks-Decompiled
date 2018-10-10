# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_util.py
import sys
import unittest
from test.test_support import run_unittest
from distutils.errors import DistutilsByteCompileError
from distutils.util import byte_compile, grok_environment_error

class UtilTestCase(unittest.TestCase):

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


def test_suite():
    return unittest.makeSuite(UtilTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
