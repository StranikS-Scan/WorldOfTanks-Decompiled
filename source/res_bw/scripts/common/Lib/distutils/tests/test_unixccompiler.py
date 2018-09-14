# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_unixccompiler.py
"""Tests for distutils.unixccompiler."""
import os
import sys
import unittest
from test.test_support import EnvironmentVarGuard, run_unittest
from distutils import sysconfig
from distutils.unixccompiler import UnixCCompiler

class UnixCCompilerTestCase(unittest.TestCase):

    def setUp(self):
        self._backup_platform = sys.platform
        self._backup_get_config_var = sysconfig.get_config_var

        class CompilerWrapper(UnixCCompiler):

            def rpath_foo(self):
                return self.runtime_library_dir_option('/foo')

        self.cc = CompilerWrapper()

    def tearDown(self):
        sys.platform = self._backup_platform
        sysconfig.get_config_var = self._backup_get_config_var

    @unittest.skipIf(sys.platform == 'win32', "can't test on Windows")
    def test_runtime_libdir_option(self):
        sys.platform = 'darwin'
        self.assertEqual(self.cc.rpath_foo(), '-L/foo')
        sys.platform = 'hp-ux'
        old_gcv = sysconfig.get_config_var

        def gcv(v):
            pass

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['+s', '-L/foo'])

        def gcv(v):
            pass

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['-Wl,+s', '-L/foo'])

        def gcv(v):
            pass

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), ['-Wl,+s', '-L/foo'])
        sysconfig.get_config_var = old_gcv
        sys.platform = 'irix646'
        self.assertEqual(self.cc.rpath_foo(), ['-rpath', '/foo'])
        sys.platform = 'osf1V5'
        self.assertEqual(self.cc.rpath_foo(), ['-rpath', '/foo'])
        sys.platform = 'bar'

        def gcv(v):
            if v == 'CC':
                return 'gcc'
            return 'yes' if v == 'GNULD' else None

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,-R/foo')
        sys.platform = 'bar'

        def gcv(v):
            if v == 'CC':
                return 'gcc'
            return 'no' if v == 'GNULD' else None

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,-R/foo')
        sys.platform = 'bar'

        def gcv(v):
            if v == 'CC':
                return 'x86_64-pc-linux-gnu-gcc-4.4.2'
            return 'yes' if v == 'GNULD' else None

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-Wl,-R/foo')
        sys.platform = 'bar'

        def gcv(v):
            if v == 'CC':
                return 'cc'
            return 'yes' if v == 'GNULD' else None

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-R/foo')
        sys.platform = 'bar'

        def gcv(v):
            if v == 'CC':
                return 'cc'
            return 'no' if v == 'GNULD' else None

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-R/foo')
        sys.platform = 'aix'

        def gcv(v):
            pass

        sysconfig.get_config_var = gcv
        self.assertEqual(self.cc.rpath_foo(), '-R/foo')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant for OS X')
    def test_osx_cc_overrides_ldshared(self):

        def gcv(v):
            return 'gcc-4.2 -bundle -undefined dynamic_lookup ' if v == 'LDSHARED' else 'gcc-4.2'

        sysconfig.get_config_var = gcv
        with EnvironmentVarGuard() as env:
            env['CC'] = 'my_cc'
            del env['LDSHARED']
            sysconfig.customize_compiler(self.cc)
        self.assertEqual(self.cc.linker_so[0], 'my_cc')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant for OS X')
    def test_osx_explict_ldshared(self):

        def gcv(v):
            return 'gcc-4.2 -bundle -undefined dynamic_lookup ' if v == 'LDSHARED' else 'gcc-4.2'

        sysconfig.get_config_var = gcv
        with EnvironmentVarGuard() as env:
            env['CC'] = 'my_cc'
            env['LDSHARED'] = 'my_ld -bundle -dynamic'
            sysconfig.customize_compiler(self.cc)
        self.assertEqual(self.cc.linker_so[0], 'my_ld')


def test_suite():
    return unittest.makeSuite(UnixCCompilerTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
