# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_sysconfig.py
# Compiled at: 2010-10-21 18:49:01
"""Tests for distutils.dist."""
from distutils import sysconfig
import os
import test
import unittest
from test.test_support import TESTFN

class SysconfigTestCase(unittest.TestCase):

    def setUp(self):
        super(SysconfigTestCase, self).setUp()
        self.makefile = None
        return

    def tearDown(self):
        if self.makefile is not None:
            os.unlink(self.makefile)
        super(SysconfigTestCase, self).tearDown()
        return

    def test_get_config_h_filename(self):
        config_h = sysconfig.get_config_h_filename()
        self.assert_(os.path.isfile(config_h), config_h)

    def test_get_python_lib(self):
        lib_dir = sysconfig.get_python_lib()
        self.assertNotEqual(sysconfig.get_python_lib(), sysconfig.get_python_lib(prefix=TESTFN))

    def test_get_python_inc(self):
        inc_dir = sysconfig.get_python_inc()
        self.assertTrue(os.path.isdir(inc_dir), inc_dir)
        python_h = os.path.join(inc_dir, 'Python.h')
        self.assertTrue(os.path.isfile(python_h), python_h)

    def test_get_config_vars(self):
        cvars = sysconfig.get_config_vars()
        self.assert_(isinstance(cvars, dict))
        self.assert_(cvars)

    def test_parse_makefile_literal_dollar(self):
        self.makefile = test.test_support.TESTFN
        fd = open(self.makefile, 'w')
        fd.write("CONFIG_ARGS=  '--arg1=optarg1' 'ENV=\\$$LIB'\n")
        fd.write('VAR=$OTHER\nOTHER=foo')
        fd.close()
        d = sysconfig.parse_makefile(self.makefile)
        self.assertEquals(d, {'CONFIG_ARGS': "'--arg1=optarg1' 'ENV=\\$LIB'",
         'OTHER': 'foo'})


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysconfigTestCase))
    return suite


if __name__ == '__main__':
    test.test_support.run_unittest(test_suite())
