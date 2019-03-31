# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_upload.py
# Compiled at: 2010-10-21 18:49:01
"""Tests for distutils.command.upload."""
import sys
import os
import unittest
from distutils.command.upload import upload
from distutils.core import Distribution
from distutils.tests import support
from distutils.tests.test_config import PYPIRC, PyPIRCCommandTestCase

class uploadTestCase(PyPIRCCommandTestCase):

    def test_finalize_options(self):
        f = open(self.rc, 'w')
        f.write(PYPIRC)
        f.close()
        dist = Distribution()
        cmd = upload(dist)
        cmd.finalize_options()
        for attr, waited in (('username', 'me'),
         ('password', 'secret'),
         ('realm', 'pypi'),
         ('repository', 'http://pypi.python.org/pypi')):
            self.assertEquals(getattr(cmd, attr), waited)


def test_suite():
    return unittest.makeSuite(uploadTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
