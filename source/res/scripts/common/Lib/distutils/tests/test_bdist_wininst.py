# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_bdist_wininst.py
import unittest
from test.test_support import run_unittest
from distutils.command.bdist_wininst import bdist_wininst
from distutils.tests import support

class BuildWinInstTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def test_get_exe_bytes(self):
        pkg_pth, dist = self.create_dist()
        cmd = bdist_wininst(dist)
        cmd.ensure_finalized()
        exe_file = cmd.get_exe_bytes()
        self.assertGreater(len(exe_file), 10)


def test_suite():
    return unittest.makeSuite(BuildWinInstTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
