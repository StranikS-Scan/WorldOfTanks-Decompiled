# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_filelist.py
# Compiled at: 2010-10-21 18:49:01
"""Tests for distutils.filelist."""
import unittest
from distutils.filelist import glob_to_re

class FileListTestCase(unittest.TestCase):

    def test_glob_to_re(self):
        self.assertEquals(glob_to_re('foo*'), 'foo[^/]*$')
        self.assertEquals(glob_to_re('foo?'), 'foo[^/]$')
        self.assertEquals(glob_to_re('foo??'), 'foo[^/][^/]$')
        self.assertEquals(glob_to_re('foo\\\\*'), 'foo\\\\\\\\[^/]*$')
        self.assertEquals(glob_to_re('foo\\\\\\*'), 'foo\\\\\\\\\\\\[^/]*$')
        self.assertEquals(glob_to_re('foo????'), 'foo[^/][^/][^/][^/]$')
        self.assertEquals(glob_to_re('foo\\\\??'), 'foo\\\\\\\\[^/][^/]$')


def test_suite():
    return unittest.makeSuite(FileListTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
