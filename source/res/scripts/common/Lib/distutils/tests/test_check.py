# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_check.py
"""Tests for distutils.command.check."""
import unittest
from test.test_support import run_unittest
from distutils.command.check import check, HAS_DOCUTILS
from distutils.tests import support
from distutils.errors import DistutilsSetupError

class CheckTestCase(support.LoggingSilencer, support.TempdirManager, unittest.TestCase):

    def _run(self, metadata=None, **options):
        if metadata is None:
            metadata = {}
        pkg_info, dist = self.create_dist(**metadata)
        cmd = check(dist)
        cmd.initialize_options()
        for name, value in options.items():
            setattr(cmd, name, value)

        cmd.ensure_finalized()
        cmd.run()
        return cmd

    def test_check_metadata(self):
        cmd = self._run()
        self.assertEqual(cmd._warnings, 2)
        metadata = {'url': 'xxx',
         'author': 'xxx',
         'author_email': 'xxx',
         'name': 'xxx',
         'version': 'xxx'}
        cmd = self._run(metadata)
        self.assertEqual(cmd._warnings, 0)
        self.assertRaises(DistutilsSetupError, self._run, {}, **{'strict': 1})
        cmd = self._run(metadata, strict=1)
        self.assertEqual(cmd._warnings, 0)
        metadata = {'url': u'xxx',
         'author': u'\xc9ric',
         'author_email': u'xxx',
         u'name': 'xxx',
         'version': u'xxx',
         'description': u'Something about esszet \xdf',
         'long_description': u'More things about esszet \xdf'}
        cmd = self._run(metadata)
        self.assertEqual(cmd._warnings, 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    def test_check_document(self):
        pkg_info, dist = self.create_dist()
        cmd = check(dist)
        broken_rest = 'title\n===\n\ntest'
        msgs = cmd._check_rst_data(broken_rest)
        self.assertEqual(len(msgs), 1)
        rest = 'title\n=====\n\ntest'
        msgs = cmd._check_rst_data(rest)
        self.assertEqual(len(msgs), 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    def test_check_restructuredtext(self):
        broken_rest = 'title\n===\n\ntest'
        pkg_info, dist = self.create_dist(long_description=broken_rest)
        cmd = check(dist)
        cmd.check_restructuredtext()
        self.assertEqual(cmd._warnings, 1)
        metadata = {'url': 'xxx',
         'author': 'xxx',
         'author_email': 'xxx',
         'name': 'xxx',
         'version': 'xxx',
         'long_description': broken_rest}
        self.assertRaises(DistutilsSetupError, self._run, metadata, **{'strict': 1,
         'restructuredtext': 1})
        metadata['long_description'] = u'title\n=====\n\ntest \xdf'
        cmd = self._run(metadata, strict=1, restructuredtext=1)
        self.assertEqual(cmd._warnings, 0)

    def test_check_all(self):
        metadata = {'url': 'xxx',
         'author': 'xxx'}
        self.assertRaises(DistutilsSetupError, self._run, {}, **{'strict': 1,
         'restructuredtext': 1})


def test_suite():
    return unittest.makeSuite(CheckTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
