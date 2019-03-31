# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_sdist.py
# Compiled at: 2010-10-21 18:49:01
"""Tests for distutils.command.sdist."""
import os
import unittest
import shutil
import zipfile
from os.path import join
import sys
from distutils.command.sdist import sdist
from distutils.core import Distribution
from distutils.tests.test_config import PyPIRCCommandTestCase
from distutils.errors import DistutilsExecError
from distutils.spawn import find_executable
SETUP_PY = "\nfrom distutils.core import setup\nimport somecode\n\nsetup(name='fake')\n"
MANIFEST_IN = '\nrecursive-include somecode *\n'

class sdistTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        super(sdistTestCase, self).setUp()
        self.old_path = os.getcwd()
        self.temp_pkg = os.path.join(self.mkdtemp(), 'temppkg')

    def tearDown(self):
        os.chdir(self.old_path)
        super(sdistTestCase, self).tearDown()

    def _init_tmp_pkg(self):
        if os.path.exists(self.temp_pkg):
            shutil.rmtree(self.temp_pkg)
        os.mkdir(self.temp_pkg)
        os.mkdir(join(self.temp_pkg, 'somecode'))
        os.mkdir(join(self.temp_pkg, 'dist'))
        self._write(join(self.temp_pkg, 'MANIFEST.in'), MANIFEST_IN)
        self._write(join(self.temp_pkg, 'README'), 'xxx')
        self._write(join(self.temp_pkg, 'somecode', '__init__.py'), '#')
        self._write(join(self.temp_pkg, 'setup.py'), SETUP_PY)
        os.chdir(self.temp_pkg)

    def _write(self, path, content):
        f = open(path, 'w')
        try:
            f.write(content)
        finally:
            f.close()

    def test_prune_file_list(self):
        self._init_tmp_pkg()
        os.mkdir(join(self.temp_pkg, 'somecode', '.svn'))
        self._write(join(self.temp_pkg, 'somecode', '.svn', 'ok.py'), 'xxx')
        os.mkdir(join(self.temp_pkg, 'somecode', '.hg'))
        self._write(join(self.temp_pkg, 'somecode', '.hg', 'ok'), 'xxx')
        os.mkdir(join(self.temp_pkg, 'somecode', '.git'))
        self._write(join(self.temp_pkg, 'somecode', '.git', 'ok'), 'xxx')
        dist = Distribution()
        dist.script_name = 'setup.py'
        dist.metadata.name = 'fake'
        dist.metadata.version = '1.0'
        dist.metadata.url = 'http://xxx'
        dist.metadata.author = dist.metadata.author_email = 'xxx'
        dist.packages = ['somecode']
        dist.include_package_data = True
        cmd = sdist(dist)
        cmd.manifest = 'MANIFEST'
        cmd.template = 'MANIFEST.in'
        cmd.dist_dir = 'dist'
        cmd.formats = ['zip']
        cmd.run()
        dist_folder = join(self.temp_pkg, 'dist')
        files = os.listdir(dist_folder)
        self.assertEquals(files, ['fake-1.0.zip'])
        zip_file = zipfile.ZipFile(join(dist_folder, 'fake-1.0.zip'))
        try:
            content = zip_file.namelist()
        finally:
            zip_file.close()

        self.assertEquals(len(content), 4)

    def test_make_distribution(self):
        if find_executable('tar') is None or find_executable('gzip') is None:
            return
        else:
            self._init_tmp_pkg()
            dist = Distribution()
            dist.script_name = 'setup.py'
            dist.metadata.name = 'fake'
            dist.metadata.version = '1.0'
            dist.metadata.url = 'http://xxx'
            dist.metadata.author = dist.metadata.author_email = 'xxx'
            dist.packages = ['somecode']
            dist.include_package_data = True
            cmd = sdist(dist)
            cmd.manifest = 'MANIFEST'
            cmd.template = 'MANIFEST.in'
            cmd.dist_dir = 'dist'
            cmd.formats = ['gztar', 'tar']
            cmd.run()
            dist_folder = join(self.temp_pkg, 'dist')
            result = os.listdir(dist_folder)
            result.sort()
            self.assertEquals(result, ['fake-1.0.tar', 'fake-1.0.tar.gz'])
            os.remove(join(dist_folder, 'fake-1.0.tar'))
            os.remove(join(dist_folder, 'fake-1.0.tar.gz'))
            cmd.formats = ['tar', 'gztar']
            cmd.run()
            result = os.listdir(dist_folder)
            result.sort()
            self.assertEquals(result, ['fake-1.0.tar', 'fake-1.0.tar.gz'])
            return


def test_suite():
    return unittest.makeSuite(sdistTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
