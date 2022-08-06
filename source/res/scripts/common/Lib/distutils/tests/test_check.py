# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_check.py
import os
import textwrap
import unittest
from test.test_support import run_unittest
from distutils.command.check import check, HAS_DOCUTILS
from distutils.tests import support
from distutils.errors import DistutilsSetupError
try:
    import pygments
except ImportError:
    pygments = None

HERE = os.path.dirname(__file__)

class CheckTestCase(support.LoggingSilencer, support.TempdirManager, unittest.TestCase):

    def _run(self, metadata=None, cwd=None, **options):
        if metadata is None:
            metadata = {}
        if cwd is not None:
            old_dir = os.getcwd()
            os.chdir(cwd)
        pkg_info, dist = self.create_dist(**metadata)
        cmd = check(dist)
        cmd.initialize_options()
        for name, value in options.items():
            setattr(cmd, name, value)

        cmd.ensure_finalized()
        cmd.run()
        if cwd is not None:
            os.chdir(old_dir)
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
        metadata['long_description'] = 'title\n=====\n\n.. include:: includetest.rst'
        cmd = self._run(metadata, cwd=HERE, strict=1, restructuredtext=1)
        self.assertEqual(cmd._warnings, 0)

    @unittest.skipUnless(HAS_DOCUTILS, "won't test without docutils")
    def test_check_restructuredtext_with_syntax_highlight(self):
        example_rst_docs = []
        example_rst_docs.append(textwrap.dedent("            Here's some code:\n\n            .. code:: python\n\n                def foo():\n                    pass\n            "))
        example_rst_docs.append(textwrap.dedent("            Here's some code:\n\n            .. code-block:: python\n\n                def foo():\n                    pass\n            "))
        for rest_with_code in example_rst_docs:
            pkg_info, dist = self.create_dist(long_description=rest_with_code)
            cmd = check(dist)
            cmd.check_restructuredtext()
            msgs = cmd._check_rst_data(rest_with_code)
            if pygments is not None:
                self.assertEqual(len(msgs), 0)
            self.assertEqual(len(msgs), 1)
            self.assertEqual(str(msgs[0][1]), 'Cannot analyze code. Pygments package not found.')

        return

    def test_check_all(self):
        metadata = {'url': 'xxx',
         'author': 'xxx'}
        self.assertRaises(DistutilsSetupError, self._run, {}, **{'strict': 1,
         'restructuredtext': 1})


def test_suite():
    return unittest.makeSuite(CheckTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
