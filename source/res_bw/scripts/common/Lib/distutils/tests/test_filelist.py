# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_filelist.py
"""Tests for distutils.filelist."""
import os
import re
import unittest
from distutils import debug
from distutils.log import WARN
from distutils.errors import DistutilsTemplateError
from distutils.filelist import glob_to_re, translate_pattern, FileList
from test.test_support import captured_stdout, run_unittest
from distutils.tests import support
MANIFEST_IN = 'include ok\ninclude xo\nexclude xo\ninclude foo.tmp\ninclude buildout.cfg\nglobal-include *.x\nglobal-include *.txt\nglobal-exclude *.tmp\nrecursive-include f *.oo\nrecursive-exclude global *.x\ngraft dir\nprune dir3\n'

def make_local_path(s):
    """Converts '/' in a string to os.sep"""
    return s.replace('/', os.sep)


class FileListTestCase(support.LoggingSilencer, unittest.TestCase):

    def assertNoWarnings(self):
        self.assertEqual(self.get_logs(WARN), [])
        self.clear_logs()

    def assertWarnings(self):
        self.assertGreater(len(self.get_logs(WARN)), 0)
        self.clear_logs()

    def test_glob_to_re(self):
        sep = os.sep
        if os.sep == '\\':
            sep = re.escape(os.sep)
        for glob, regex in (('foo*', 'foo[^%(sep)s]*\\Z(?ms)'),
         ('foo?', 'foo[^%(sep)s]\\Z(?ms)'),
         ('foo??', 'foo[^%(sep)s][^%(sep)s]\\Z(?ms)'),
         ('foo\\\\*', 'foo\\\\\\\\[^%(sep)s]*\\Z(?ms)'),
         ('foo\\\\\\*', 'foo\\\\\\\\\\\\[^%(sep)s]*\\Z(?ms)'),
         ('foo????', 'foo[^%(sep)s][^%(sep)s][^%(sep)s][^%(sep)s]\\Z(?ms)'),
         ('foo\\\\??', 'foo\\\\\\\\[^%(sep)s][^%(sep)s]\\Z(?ms)')):
            regex = regex % {'sep': sep}
            self.assertEqual(glob_to_re(glob), regex)

    def test_process_template_line(self):
        file_list = FileList()
        l = make_local_path
        file_list.allfiles = ['foo.tmp',
         'ok',
         'xo',
         'four.txt',
         'buildout.cfg',
         l('.hg/last-message.txt'),
         l('global/one.txt'),
         l('global/two.txt'),
         l('global/files.x'),
         l('global/here.tmp'),
         l('f/o/f.oo'),
         l('dir/graft-one'),
         l('dir/dir2/graft2'),
         l('dir3/ok'),
         l('dir3/sub/ok.txt')]
        for line in MANIFEST_IN.split('\n'):
            if line.strip() == '':
                continue
            file_list.process_template_line(line)

        wanted = ['ok',
         'buildout.cfg',
         'four.txt',
         l('.hg/last-message.txt'),
         l('global/one.txt'),
         l('global/two.txt'),
         l('f/o/f.oo'),
         l('dir/graft-one'),
         l('dir/dir2/graft2')]
        self.assertEqual(file_list.files, wanted)

    def test_debug_print(self):
        file_list = FileList()
        with captured_stdout() as stdout:
            file_list.debug_print('xxx')
        self.assertEqual(stdout.getvalue(), '')
        debug.DEBUG = True
        try:
            with captured_stdout() as stdout:
                file_list.debug_print('xxx')
            self.assertEqual(stdout.getvalue(), 'xxx\n')
        finally:
            debug.DEBUG = False

    def test_set_allfiles(self):
        file_list = FileList()
        files = ['a', 'b', 'c']
        file_list.set_allfiles(files)
        self.assertEqual(file_list.allfiles, files)

    def test_remove_duplicates(self):
        file_list = FileList()
        file_list.files = ['a',
         'b',
         'a',
         'g',
         'c',
         'g']
        file_list.sort()
        file_list.remove_duplicates()
        self.assertEqual(file_list.files, ['a',
         'b',
         'c',
         'g'])

    def test_translate_pattern(self):
        self.assertTrue(hasattr(translate_pattern('a', anchor=True, is_regex=False), 'search'))
        regex = re.compile('a')
        self.assertEqual(translate_pattern(regex, anchor=True, is_regex=True), regex)
        self.assertTrue(hasattr(translate_pattern('a', anchor=True, is_regex=True), 'search'))
        self.assertTrue(translate_pattern('*.py', anchor=True, is_regex=False).search('filelist.py'))

    def test_exclude_pattern(self):
        file_list = FileList()
        self.assertFalse(file_list.exclude_pattern('*.py'))
        file_list = FileList()
        file_list.files = ['a.py', 'b.py']
        self.assertTrue(file_list.exclude_pattern('*.py'))
        file_list = FileList()
        file_list.files = ['a.py', 'a.txt']
        file_list.exclude_pattern('*.py')
        self.assertEqual(file_list.files, ['a.txt'])

    def test_include_pattern(self):
        file_list = FileList()
        file_list.set_allfiles([])
        self.assertFalse(file_list.include_pattern('*.py'))
        file_list = FileList()
        file_list.set_allfiles(['a.py', 'b.txt'])
        self.assertTrue(file_list.include_pattern('*.py'))
        file_list = FileList()
        self.assertIsNone(file_list.allfiles)
        file_list.set_allfiles(['a.py', 'b.txt'])
        file_list.include_pattern('*')
        self.assertEqual(file_list.allfiles, ['a.py', 'b.txt'])

    def test_process_template(self):
        l = make_local_path
        file_list = FileList()
        for action in ('include', 'exclude', 'global-include', 'global-exclude', 'recursive-include', 'recursive-exclude', 'graft', 'prune', 'blarg'):
            self.assertRaises(DistutilsTemplateError, file_list.process_template_line, action)

        file_list = FileList()
        file_list.set_allfiles(['a.py', 'b.txt', l('d/c.py')])
        file_list.process_template_line('include *.py')
        self.assertEqual(file_list.files, ['a.py'])
        self.assertNoWarnings()
        file_list.process_template_line('include *.rb')
        self.assertEqual(file_list.files, ['a.py'])
        self.assertWarnings()
        file_list = FileList()
        file_list.files = ['a.py', 'b.txt', l('d/c.py')]
        file_list.process_template_line('exclude *.py')
        self.assertEqual(file_list.files, ['b.txt', l('d/c.py')])
        self.assertNoWarnings()
        file_list.process_template_line('exclude *.rb')
        self.assertEqual(file_list.files, ['b.txt', l('d/c.py')])
        self.assertWarnings()
        file_list = FileList()
        file_list.set_allfiles(['a.py', 'b.txt', l('d/c.py')])
        file_list.process_template_line('global-include *.py')
        self.assertEqual(file_list.files, ['a.py', l('d/c.py')])
        self.assertNoWarnings()
        file_list.process_template_line('global-include *.rb')
        self.assertEqual(file_list.files, ['a.py', l('d/c.py')])
        self.assertWarnings()
        file_list = FileList()
        file_list.files = ['a.py', 'b.txt', l('d/c.py')]
        file_list.process_template_line('global-exclude *.py')
        self.assertEqual(file_list.files, ['b.txt'])
        self.assertNoWarnings()
        file_list.process_template_line('global-exclude *.rb')
        self.assertEqual(file_list.files, ['b.txt'])
        self.assertWarnings()
        file_list = FileList()
        file_list.set_allfiles(['a.py',
         l('d/b.py'),
         l('d/c.txt'),
         l('d/d/e.py')])
        file_list.process_template_line('recursive-include d *.py')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertNoWarnings()
        file_list.process_template_line('recursive-include e *.py')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertWarnings()
        file_list = FileList()
        file_list.files = ['a.py',
         l('d/b.py'),
         l('d/c.txt'),
         l('d/d/e.py')]
        file_list.process_template_line('recursive-exclude d *.py')
        self.assertEqual(file_list.files, ['a.py', l('d/c.txt')])
        self.assertNoWarnings()
        file_list.process_template_line('recursive-exclude e *.py')
        self.assertEqual(file_list.files, ['a.py', l('d/c.txt')])
        self.assertWarnings()
        file_list = FileList()
        file_list.set_allfiles(['a.py',
         l('d/b.py'),
         l('d/d/e.py'),
         l('f/f.py')])
        file_list.process_template_line('graft d')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertNoWarnings()
        file_list.process_template_line('graft e')
        self.assertEqual(file_list.files, [l('d/b.py'), l('d/d/e.py')])
        self.assertWarnings()
        file_list = FileList()
        file_list.files = ['a.py',
         l('d/b.py'),
         l('d/d/e.py'),
         l('f/f.py')]
        file_list.process_template_line('prune d')
        self.assertEqual(file_list.files, ['a.py', l('f/f.py')])
        self.assertNoWarnings()
        file_list.process_template_line('prune e')
        self.assertEqual(file_list.files, ['a.py', l('f/f.py')])
        self.assertWarnings()


def test_suite():
    return unittest.makeSuite(FileListTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
