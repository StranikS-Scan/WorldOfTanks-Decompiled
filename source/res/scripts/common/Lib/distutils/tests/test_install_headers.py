# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_install_headers.py
import sys
import os
import unittest
import getpass
from distutils.command.install_headers import install_headers
from distutils.tests import support
from test.test_support import run_unittest

class InstallHeadersTestCase(support.TempdirManager, support.LoggingSilencer, support.EnvironGuard, unittest.TestCase):

    def test_simple_run(self):
        header_list = self.mkdtemp()
        header1 = os.path.join(header_list, 'header1')
        header2 = os.path.join(header_list, 'header2')
        self.write_file(header1)
        self.write_file(header2)
        headers = [header1, header2]
        pkg_dir, dist = self.create_dist(headers=headers)
        cmd = install_headers(dist)
        self.assertEqual(cmd.get_inputs(), headers)
        cmd.install_dir = os.path.join(pkg_dir, 'inst')
        cmd.ensure_finalized()
        cmd.run()
        self.assertEqual(len(cmd.get_outputs()), 2)


def test_suite():
    return unittest.makeSuite(InstallHeadersTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
