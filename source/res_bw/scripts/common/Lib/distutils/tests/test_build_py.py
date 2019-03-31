# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_build_py.py
# Compiled at: 2010-05-25 20:46:16
"""Tests for distutils.command.build_py."""
import os
import sys
import StringIO
import unittest
from distutils.command.build_py import build_py
from distutils.core import Distribution
from distutils.errors import DistutilsFileError
from distutils.tests import support

class BuildPyTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def test_package_data(self):
        sources = self.mkdtemp()
        f = open(os.path.join(sources, '__init__.py'), 'w')
        f.write('# Pretend this is a package.')
        f.close()
        f = open(os.path.join(sources, 'README.txt'), 'w')
        f.write('Info about this package')
        f.close()
        destination = self.mkdtemp()
        dist = Distribution({'packages': ['pkg'],
         'package_dir': {'pkg': sources}})
        dist.script_name = os.path.join(sources, 'setup.py')
        dist.command_obj['build'] = support.DummyCommand(force=0, build_lib=destination)
        dist.packages = ['pkg']
        dist.package_data = {'pkg': ['README.txt']}
        dist.package_dir = {'pkg': sources}
        cmd = build_py(dist)
        cmd.compile = 1
        cmd.ensure_finalized()
        self.assertEqual(cmd.package_data, dist.package_data)
        cmd.run()
        self.assertEqual(len(cmd.get_outputs()), 3)
        pkgdest = os.path.join(destination, 'pkg')
        files = os.listdir(pkgdest)
        self.assert_('__init__.py' in files)
        self.assert_('__init__.pyc' in files)
        self.assert_('README.txt' in files)

    def test_empty_package_dir(self):
        cwd = os.getcwd()
        sources = self.mkdtemp()
        open(os.path.join(sources, '__init__.py'), 'w').close()
        testdir = os.path.join(sources, 'doc')
        os.mkdir(testdir)
        open(os.path.join(testdir, 'testfile'), 'w').close()
        os.chdir(sources)
        sys.stdout = StringIO.StringIO()
        try:
            dist = Distribution({'packages': ['pkg'],
             'package_dir': {'pkg': ''},
             'package_data': {'pkg': ['doc/*']}})
            dist.script_name = os.path.join(sources, 'setup.py')
            dist.script_args = ['build']
            dist.parse_command_line()
            try:
                dist.run_commands()
            except DistutilsFileError:
                self.fail("failed package_data test when package_dir is ''")

        finally:
            os.chdir(cwd)
            sys.stdout = sys.__stdout__


def test_suite():
    return unittest.makeSuite(BuildPyTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
