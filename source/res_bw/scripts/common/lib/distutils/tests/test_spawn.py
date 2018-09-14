# Embedded file name: scripts/common/Lib/distutils/tests/test_spawn.py
"""Tests for distutils.spawn."""
import unittest
import os
import time
from test.test_support import captured_stdout, run_unittest
from distutils.spawn import _nt_quote_args
from distutils.spawn import spawn, find_executable
from distutils.errors import DistutilsExecError
from distutils.tests import support

class SpawnTestCase(support.TempdirManager, support.LoggingSilencer, unittest.TestCase):

    def test_nt_quote_args(self):
        for args, wanted in ((['with space', 'nospace'], ['"with space"', 'nospace']), (['nochange', 'nospace'], ['nochange', 'nospace'])):
            res = _nt_quote_args(args)
            self.assertEqual(res, wanted)

    @unittest.skipUnless(os.name in ('nt', 'posix'), 'Runs only under posix or nt')
    def test_spawn(self):
        tmpdir = self.mkdtemp()
        if os.name == 'posix':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!/bin/sh\nexit 1')
            os.chmod(exe, 511)
        else:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 1')
        os.chmod(exe, 511)
        self.assertRaises(DistutilsExecError, spawn, [exe])
        if os.name == 'posix':
            exe = os.path.join(tmpdir, 'foo.sh')
            self.write_file(exe, '#!/bin/sh\nexit 0')
            os.chmod(exe, 511)
        else:
            exe = os.path.join(tmpdir, 'foo.bat')
            self.write_file(exe, 'exit 0')
        os.chmod(exe, 511)
        spawn([exe])


def test_suite():
    return unittest.makeSuite(SpawnTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
