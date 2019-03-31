# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_build_ext.py
# Compiled at: 2010-10-21 18:49:01
import sys
import os
import tempfile
import shutil
from StringIO import StringIO
from distutils.core import Extension, Distribution
from distutils.command.build_ext import build_ext
from distutils import sysconfig
from distutils.tests import support
from distutils.errors import DistutilsSetupError
import unittest
from test import test_support
ALREADY_TESTED = False

class BuildExtTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def setUp(self):
        super(BuildExtTestCase, self).setUp()
        self.tmp_dir = tempfile.mkdtemp(prefix='pythontest_')
        self.sys_path = sys.path[:]
        sys.path.append(self.tmp_dir)
        xx_c = os.path.join(sysconfig.project_base, 'Modules', 'xxmodule.c')
        shutil.copy(xx_c, self.tmp_dir)

    def test_build_ext(self):
        global ALREADY_TESTED
        xx_c = os.path.join(self.tmp_dir, 'xxmodule.c')
        xx_ext = Extension('xx', [xx_c])
        dist = Distribution({'name': 'xx',
         'ext_modules': [xx_ext]})
        dist.package_dir = self.tmp_dir
        cmd = build_ext(dist)
        if os.name == 'nt':
            cmd.debug = sys.executable.endswith('_d.exe')
        cmd.build_lib = self.tmp_dir
        cmd.build_temp = self.tmp_dir
        old_stdout = sys.stdout
        if not test_support.verbose:
            sys.stdout = StringIO()
        try:
            cmd.ensure_finalized()
            cmd.run()
        finally:
            sys.stdout = old_stdout

        if ALREADY_TESTED:
            return
        else:
            ALREADY_TESTED = True
            import xx
            for attr in ('error', 'foo', 'new', 'roj'):
                self.assert_(hasattr(xx, attr))

            self.assertEquals(xx.foo(2, 5), 7)
            self.assertEquals(xx.foo(13, 15), 28)
            self.assertEquals(xx.new().demo(), None)
            doc = 'This is a template module just for instruction.'
            self.assertEquals(xx.__doc__, doc)
            self.assert_(isinstance(xx.Null(), xx.Null))
            self.assert_(isinstance(xx.Str(), xx.Str))
            return

    def tearDown(self):
        test_support.unload('xx')
        sys.path = self.sys_path
        shutil.rmtree(self.tmp_dir, os.name == 'nt' or sys.platform == 'cygwin')
        super(BuildExtTestCase, self).tearDown()

    def test_solaris_enable_shared(self):
        dist = Distribution({'name': 'xx'})
        cmd = build_ext(dist)
        old = sys.platform
        sys.platform = 'sunos'
        from distutils.sysconfig import _config_vars
        old_var = _config_vars.get('Py_ENABLE_SHARED')
        _config_vars['Py_ENABLE_SHARED'] = 1
        try:
            cmd.ensure_finalized()
        finally:
            sys.platform = old
            if old_var is None:
                del _config_vars['Py_ENABLE_SHARED']
            else:
                _config_vars['Py_ENABLE_SHARED'] = old_var

        self.assert_(len(cmd.library_dirs) > 0)
        return

    def test_finalize_options(self):
        modules = [Extension('foo', ['xxx'])]
        dist = Distribution({'name': 'xx',
         'ext_modules': modules})
        cmd = build_ext(dist)
        cmd.finalize_options()
        from distutils import sysconfig
        py_include = sysconfig.get_python_inc()
        self.assert_(py_include in cmd.include_dirs)
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        self.assert_(plat_py_include in cmd.include_dirs)
        cmd = build_ext(dist)
        cmd.libraries = 'my_lib'
        cmd.finalize_options()
        self.assertEquals(cmd.libraries, ['my_lib'])
        cmd = build_ext(dist)
        cmd.library_dirs = 'my_lib_dir'
        cmd.finalize_options()
        self.assert_('my_lib_dir' in cmd.library_dirs)
        cmd = build_ext(dist)
        cmd.rpath = os.pathsep.join(['one', 'two'])
        cmd.finalize_options()
        self.assertEquals(cmd.rpath, ['one', 'two'])
        cmd = build_ext(dist)
        cmd.define = 'one,two'
        cmd.finalize_options()
        self.assertEquals(cmd.define, [('one', '1'), ('two', '1')])
        cmd = build_ext(dist)
        cmd.undef = 'one,two'
        cmd.finalize_options()
        self.assertEquals(cmd.undef, ['one', 'two'])
        cmd = build_ext(dist)
        cmd.swig_opts = None
        cmd.finalize_options()
        self.assertEquals(cmd.swig_opts, [])
        cmd = build_ext(dist)
        cmd.swig_opts = '1 2'
        cmd.finalize_options()
        self.assertEquals(cmd.swig_opts, ['1', '2'])
        return

    def test_check_extensions_list(self):
        dist = Distribution()
        cmd = build_ext(dist)
        cmd.finalize_options()
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, 'foo')
        exts = [('bar', 'foo', 'bar'), 'foo']
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)
        exts = [('foo-bar', '')]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)
        exts = [('foo.bar', '')]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)
        exts = [('foo.bar', {'sources': [''],
           'libraries': 'foo',
           'some': 'bar'})]
        cmd.check_extensions_list(exts)
        ext = exts[0]
        self.assert_(isinstance(ext, Extension))
        self.assertEquals(ext.libraries, 'foo')
        self.assert_(not hasattr(ext, 'some'))
        exts = [('foo.bar', {'sources': [''],
           'libraries': 'foo',
           'some': 'bar',
           'macros': [('1', '2', '3'), 'foo']})]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)
        exts[0][1]['macros'] = [('1', '2'), ('3',)]
        cmd.check_extensions_list(exts)
        self.assertEquals(exts[0].undef_macros, ['3'])
        self.assertEquals(exts[0].define_macros, [('1', '2')])

    def test_get_source_files(self):
        modules = [Extension('foo', ['xxx'])]
        dist = Distribution({'name': 'xx',
         'ext_modules': modules})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        self.assertEquals(cmd.get_source_files(), ['xxx'])

    def test_compiler_option(self):
        dist = Distribution()
        cmd = build_ext(dist)
        cmd.compiler = 'unix'
        cmd.ensure_finalized()
        cmd.run()
        self.assertEquals(cmd.compiler, 'unix')

    def test_get_outputs(self):
        tmp_dir = self.mkdtemp()
        c_file = os.path.join(tmp_dir, 'foo.c')
        self.write_file(c_file, 'void initfoo(void) {};\n')
        ext = Extension('foo', [c_file])
        dist = Distribution({'name': 'xx',
         'ext_modules': [ext]})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        self.assertEquals(len(cmd.get_outputs()), 1)
        if os.name == 'nt':
            cmd.debug = sys.executable.endswith('_d.exe')
        cmd.build_lib = os.path.join(self.tmp_dir, 'build')
        cmd.build_temp = os.path.join(self.tmp_dir, 'tempt')
        other_tmp_dir = os.path.realpath(self.mkdtemp())
        old_wd = os.getcwd()
        os.chdir(other_tmp_dir)
        try:
            cmd.inplace = 1
            cmd.run()
            so_file = cmd.get_outputs()[0]
        finally:
            os.chdir(old_wd)

        self.assert_(os.path.exists(so_file))
        self.assertEquals(os.path.splitext(so_file)[-1], sysconfig.get_config_var('SO'))
        so_dir = os.path.dirname(so_file)
        self.assertEquals(so_dir, other_tmp_dir)
        cmd.compiler = None
        cmd.inplace = 0
        cmd.run()
        so_file = cmd.get_outputs()[0]
        self.assert_(os.path.exists(so_file))
        self.assertEquals(os.path.splitext(so_file)[-1], sysconfig.get_config_var('SO'))
        so_dir = os.path.dirname(so_file)
        self.assertEquals(so_dir, cmd.build_lib)
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {'': 'bar'}
        path = cmd.get_ext_fullpath('foo')
        path = os.path.split(path)[0]
        self.assertEquals(path, cmd.build_lib)
        cmd.inplace = 1
        other_tmp_dir = os.path.realpath(self.mkdtemp())
        old_wd = os.getcwd()
        os.chdir(other_tmp_dir)
        try:
            path = cmd.get_ext_fullpath('foo')
        finally:
            os.chdir(old_wd)

        path = os.path.split(path)[0]
        lastdir = os.path.split(path)[-1]
        self.assertEquals(lastdir, 'bar')
        return

    def test_ext_fullpath(self):
        ext = sysconfig.get_config_vars()['SO']
        dist = Distribution()
        cmd = build_ext(dist)
        cmd.inplace = 1
        cmd.distribution.package_dir = {'': 'src'}
        cmd.distribution.packages = ['lxml', 'lxml.html']
        curdir = os.getcwd()
        wanted = os.path.join(curdir, 'src', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEquals(wanted, path)
        cmd.inplace = 0
        cmd.build_lib = os.path.join(curdir, 'tmpdir')
        wanted = os.path.join(curdir, 'tmpdir', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEquals(wanted, path)
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {}
        cmd.distribution.packages = ['twisted', 'twisted.runner.portmap']
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'tmpdir', 'twisted', 'runner', 'portmap' + ext)
        self.assertEquals(wanted, path)
        cmd.inplace = 1
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'twisted', 'runner', 'portmap' + ext)
        self.assertEquals(wanted, path)

    def test_build_ext_inplace(self):
        etree_c = os.path.join(self.tmp_dir, 'lxml.etree.c')
        etree_ext = Extension('lxml.etree', [etree_c])
        dist = Distribution({'name': 'lxml',
         'ext_modules': [etree_ext]})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        cmd.inplace = 1
        cmd.distribution.package_dir = {'': 'src'}
        cmd.distribution.packages = ['lxml', 'lxml.html']
        curdir = os.getcwd()
        ext = sysconfig.get_config_var('SO')
        wanted = os.path.join(curdir, 'src', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEquals(wanted, path)

    def test_setuptools_compat(self):
        from setuptools_build_ext import build_ext as setuptools_build_ext
        from setuptools_extension import Extension
        etree_c = os.path.join(self.tmp_dir, 'lxml.etree.c')
        etree_ext = Extension('lxml.etree', [etree_c])
        dist = Distribution({'name': 'lxml',
         'ext_modules': [etree_ext]})
        cmd = setuptools_build_ext(dist)
        cmd.ensure_finalized()
        cmd.inplace = 1
        cmd.distribution.package_dir = {'': 'src'}
        cmd.distribution.packages = ['lxml', 'lxml.html']
        curdir = os.getcwd()
        ext = sysconfig.get_config_var('SO')
        wanted = os.path.join(curdir, 'src', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEquals(wanted, path)

    def test_build_ext_path_with_os_sep(self):
        dist = Distribution({'name': 'UpdateManager'})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        ext = sysconfig.get_config_var('SO')
        ext_name = os.path.join('UpdateManager', 'fdsend')
        ext_path = cmd.get_ext_fullpath(ext_name)
        wanted = os.path.join(cmd.build_lib, 'UpdateManager', 'fdsend' + ext)
        self.assertEquals(ext_path, wanted)

    def test_build_ext_path_cross_platform(self):
        if sys.platform != 'win32':
            return
        dist = Distribution({'name': 'UpdateManager'})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        ext = sysconfig.get_config_var('SO')
        ext_name = 'UpdateManager/fdsend'
        ext_path = cmd.get_ext_fullpath(ext_name)
        wanted = os.path.join(cmd.build_lib, 'UpdateManager', 'fdsend' + ext)
        self.assertEquals(ext_path, wanted)


def test_suite():
    if not sysconfig.python_build:
        if test_support.verbose:
            print 'test_build_ext: The test must be run in a python build dir'
        return unittest.TestSuite()
    else:
        return unittest.makeSuite(BuildExtTestCase)


if __name__ == '__main__':
    test_support.run_unittest(test_suite())
