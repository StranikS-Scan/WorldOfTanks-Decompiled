# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_build_ext.py
import sys
import os
from StringIO import StringIO
import textwrap
from distutils.core import Extension, Distribution
from distutils.command.build_ext import build_ext
from distutils import sysconfig
from distutils.tests import support
from distutils.errors import DistutilsSetupError, CompileError, DistutilsPlatformError
import unittest
from test import test_support
ALREADY_TESTED = False

class BuildExtTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def setUp(self):
        super(BuildExtTestCase, self).setUp()
        self.tmp_dir = self.mkdtemp()
        self.xx_created = False
        sys.path.append(self.tmp_dir)
        self.addCleanup(sys.path.remove, self.tmp_dir)
        if sys.version > '2.6':
            import site
            self.old_user_base = site.USER_BASE
            site.USER_BASE = self.mkdtemp()
            from distutils.command import build_ext
            build_ext.USER_BASE = site.USER_BASE

    def tearDown(self):
        if self.xx_created:
            test_support.unload('xx')
        super(BuildExtTestCase, self).tearDown()

    def test_build_ext(self):
        global ALREADY_TESTED
        support.copy_xxmodule_c(self.tmp_dir)
        self.xx_created = True
        xx_c = os.path.join(self.tmp_dir, 'xxmodule.c')
        xx_ext = Extension('xx', [xx_c])
        dist = Distribution({'name': 'xx',
         'ext_modules': [xx_ext]})
        dist.package_dir = self.tmp_dir
        cmd = build_ext(dist)
        support.fixup_build_ext(cmd)
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
            self.skipTest('Already tested in %s' % ALREADY_TESTED)
        else:
            ALREADY_TESTED = type(self).__name__
        import xx
        for attr in ('error', 'foo', 'new', 'roj'):
            self.assertTrue(hasattr(xx, attr))

        self.assertEqual(xx.foo(2, 5), 7)
        self.assertEqual(xx.foo(13, 15), 28)
        self.assertEqual(xx.new().demo(), None)
        if test_support.HAVE_DOCSTRINGS:
            doc = 'This is a template module just for instruction.'
            self.assertEqual(xx.__doc__, doc)
        self.assertIsInstance(xx.Null(), xx.Null)
        self.assertIsInstance(xx.Str(), xx.Str)
        return

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

        self.assertGreater(len(cmd.library_dirs), 0)
        return

    @unittest.skipIf(sys.version < '2.6', 'site.USER_SITE was introduced in 2.6')
    def test_user_site(self):
        import site
        dist = Distribution({'name': 'xx'})
        cmd = build_ext(dist)
        options = [ name for name, short, label in cmd.user_options ]
        self.assertIn('user', options)
        cmd.user = 1
        lib = os.path.join(site.USER_BASE, 'lib')
        incl = os.path.join(site.USER_BASE, 'include')
        os.mkdir(lib)
        os.mkdir(incl)
        cmd.ensure_finalized()
        self.assertIn(lib, cmd.library_dirs)
        self.assertIn(lib, cmd.rpath)
        self.assertIn(incl, cmd.include_dirs)

    def test_finalize_options(self):
        modules = [Extension('foo', ['xxx'])]
        dist = Distribution({'name': 'xx',
         'ext_modules': modules})
        cmd = build_ext(dist)
        cmd.finalize_options()
        py_include = sysconfig.get_python_inc()
        self.assertIn(py_include, cmd.include_dirs)
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        self.assertIn(plat_py_include, cmd.include_dirs)
        cmd = build_ext(dist)
        cmd.libraries = 'my_lib, other_lib lastlib'
        cmd.finalize_options()
        self.assertEqual(cmd.libraries, ['my_lib', 'other_lib', 'lastlib'])
        cmd = build_ext(dist)
        cmd.library_dirs = 'my_lib_dir%sother_lib_dir' % os.pathsep
        cmd.finalize_options()
        self.assertIn('my_lib_dir', cmd.library_dirs)
        self.assertIn('other_lib_dir', cmd.library_dirs)
        cmd = build_ext(dist)
        cmd.rpath = 'one%stwo' % os.pathsep
        cmd.finalize_options()
        self.assertEqual(cmd.rpath, ['one', 'two'])
        cmd = build_ext(dist)
        cmd.define = 'one,two'
        cmd.finalize_options()
        self.assertEqual(cmd.define, [('one', '1'), ('two', '1')])
        cmd = build_ext(dist)
        cmd.undef = 'one,two'
        cmd.finalize_options()
        self.assertEqual(cmd.undef, ['one', 'two'])
        cmd = build_ext(dist)
        cmd.swig_opts = None
        cmd.finalize_options()
        self.assertEqual(cmd.swig_opts, [])
        cmd = build_ext(dist)
        cmd.swig_opts = '1 2'
        cmd.finalize_options()
        self.assertEqual(cmd.swig_opts, ['1', '2'])
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
        self.assertIsInstance(ext, Extension)
        self.assertEqual(ext.libraries, 'foo')
        self.assertFalse(hasattr(ext, 'some'))
        exts = [('foo.bar', {'sources': [''],
           'libraries': 'foo',
           'some': 'bar',
           'macros': [('1', '2', '3'), 'foo']})]
        self.assertRaises(DistutilsSetupError, cmd.check_extensions_list, exts)
        exts[0][1]['macros'] = [('1', '2'), ('3',)]
        cmd.check_extensions_list(exts)
        self.assertEqual(exts[0].undef_macros, ['3'])
        self.assertEqual(exts[0].define_macros, [('1', '2')])

    def test_get_source_files(self):
        modules = [Extension('foo', ['xxx'])]
        dist = Distribution({'name': 'xx',
         'ext_modules': modules})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        self.assertEqual(cmd.get_source_files(), ['xxx'])

    def test_compiler_option(self):
        dist = Distribution()
        cmd = build_ext(dist)
        cmd.compiler = 'unix'
        cmd.ensure_finalized()
        cmd.run()
        self.assertEqual(cmd.compiler, 'unix')

    def test_get_outputs(self):
        tmp_dir = self.mkdtemp()
        c_file = os.path.join(tmp_dir, 'foo.c')
        self.write_file(c_file, 'void initfoo(void) {};\n')
        ext = Extension('foo', [c_file])
        dist = Distribution({'name': 'xx',
         'ext_modules': [ext]})
        cmd = build_ext(dist)
        support.fixup_build_ext(cmd)
        cmd.ensure_finalized()
        self.assertEqual(len(cmd.get_outputs()), 1)
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

        self.assertTrue(os.path.exists(so_file))
        self.assertEqual(os.path.splitext(so_file)[-1], sysconfig.get_config_var('SO'))
        so_dir = os.path.dirname(so_file)
        self.assertEqual(so_dir, other_tmp_dir)
        cmd.compiler = None
        cmd.inplace = 0
        cmd.run()
        so_file = cmd.get_outputs()[0]
        self.assertTrue(os.path.exists(so_file))
        self.assertEqual(os.path.splitext(so_file)[-1], sysconfig.get_config_var('SO'))
        so_dir = os.path.dirname(so_file)
        self.assertEqual(so_dir, cmd.build_lib)
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {'': 'bar'}
        path = cmd.get_ext_fullpath('foo')
        path = os.path.split(path)[0]
        self.assertEqual(path, cmd.build_lib)
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
        self.assertEqual(lastdir, 'bar')
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
        self.assertEqual(wanted, path)
        cmd.inplace = 0
        cmd.build_lib = os.path.join(curdir, 'tmpdir')
        wanted = os.path.join(curdir, 'tmpdir', 'lxml', 'etree' + ext)
        path = cmd.get_ext_fullpath('lxml.etree')
        self.assertEqual(wanted, path)
        build_py = cmd.get_finalized_command('build_py')
        build_py.package_dir = {}
        cmd.distribution.packages = ['twisted', 'twisted.runner.portmap']
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'tmpdir', 'twisted', 'runner', 'portmap' + ext)
        self.assertEqual(wanted, path)
        cmd.inplace = 1
        path = cmd.get_ext_fullpath('twisted.runner.portmap')
        wanted = os.path.join(curdir, 'twisted', 'runner', 'portmap' + ext)
        self.assertEqual(wanted, path)

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
        self.assertEqual(wanted, path)

    def test_setuptools_compat(self):
        import distutils.core, distutils.extension, distutils.command.build_ext
        saved_ext = distutils.extension.Extension
        try:
            test_support.import_module('setuptools_build_ext', deprecated=True)
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
            self.assertEqual(wanted, path)
        finally:
            distutils.extension.Extension = saved_ext
            distutils.core.Extension = saved_ext
            distutils.command.build_ext.Extension = saved_ext

    def test_build_ext_path_with_os_sep(self):
        dist = Distribution({'name': 'UpdateManager'})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        ext = sysconfig.get_config_var('SO')
        ext_name = os.path.join('UpdateManager', 'fdsend')
        ext_path = cmd.get_ext_fullpath(ext_name)
        wanted = os.path.join(cmd.build_lib, 'UpdateManager', 'fdsend' + ext)
        self.assertEqual(ext_path, wanted)

    @unittest.skipUnless(sys.platform == 'win32', 'these tests require Windows')
    def test_build_ext_path_cross_platform(self):
        dist = Distribution({'name': 'UpdateManager'})
        cmd = build_ext(dist)
        cmd.ensure_finalized()
        ext = sysconfig.get_config_var('SO')
        ext_name = 'UpdateManager/fdsend'
        ext_path = cmd.get_ext_fullpath(ext_name)
        wanted = os.path.join(cmd.build_lib, 'UpdateManager', 'fdsend' + ext)
        self.assertEqual(ext_path, wanted)

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant for MacOSX')
    def test_deployment_target_default(self):
        self._try_compile_deployment_target('==', None)
        return

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant for MacOSX')
    def test_deployment_target_too_low(self):
        self.assertRaises(DistutilsPlatformError, self._try_compile_deployment_target, '>', '10.1')

    @unittest.skipUnless(sys.platform == 'darwin', 'test only relevant for MacOSX')
    def test_deployment_target_higher_ok(self):
        deptarget = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
        if deptarget:
            deptarget = [ int(x) for x in deptarget.split('.') ]
            deptarget[-1] += 1
            deptarget = '.'.join((str(i) for i in deptarget))
            self._try_compile_deployment_target('<', deptarget)

    def _try_compile_deployment_target(self, operator, target):
        orig_environ = os.environ
        os.environ = orig_environ.copy()
        self.addCleanup(setattr, os, 'environ', orig_environ)
        if target is None:
            if os.environ.get('MACOSX_DEPLOYMENT_TARGET'):
                del os.environ['MACOSX_DEPLOYMENT_TARGET']
        else:
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = target
        deptarget_c = os.path.join(self.tmp_dir, 'deptargetmodule.c')
        with open(deptarget_c, 'w') as fp:
            fp.write(textwrap.dedent('                #include <AvailabilityMacros.h>\n\n                int dummy;\n\n                #if TARGET %s MAC_OS_X_VERSION_MIN_REQUIRED\n                #else\n                #error "Unexpected target"\n                #endif\n\n            ' % operator))
        target = sysconfig.get_config_var('MACOSX_DEPLOYMENT_TARGET')
        target = tuple(map(int, target.split('.')))
        target = '%02d%01d0' % target
        deptarget_ext = Extension('deptarget', [deptarget_c], extra_compile_args=['-DTARGET=%s' % (target,)])
        dist = Distribution({'name': 'deptarget',
         'ext_modules': [deptarget_ext]})
        dist.package_dir = self.tmp_dir
        cmd = build_ext(dist)
        cmd.build_lib = self.tmp_dir
        cmd.build_temp = self.tmp_dir
        try:
            cmd.ensure_finalized()
            cmd.run()
        except CompileError:
            self.fail('Wrong deployment target during compilation')

        return


def test_suite():
    return unittest.makeSuite(BuildExtTestCase)


if __name__ == '__main__':
    test_support.run_unittest(test_suite())
