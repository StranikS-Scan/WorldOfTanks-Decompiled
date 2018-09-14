# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/test_grep.py
""" !Changing this line will break Test_findfile.test_found!
Non-gui unit tests for idlelib.GrepDialog methods.
dummy_command calls grep_it calls findfiles.
An exception raised in one method will fail callers.
Otherwise, tests are mostly independent.
*** Currently only test grep_it.
"""
import unittest
from test.test_support import captured_stdout, findfile
from idlelib.idle_test.mock_tk import Var
from idlelib.GrepDialog import GrepDialog
import re
__file__ = findfile('idlelib/idle_test') + '/test_grep.py'

class Dummy_searchengine:
    """GrepDialog.__init__ calls parent SearchDiabolBase which attaches the
    passed in SearchEngine instance as attribute 'engine'. Only a few of the
    many possible self.engine.x attributes are needed here.
    """

    def getpat(self):
        return self._pat


searchengine = Dummy_searchengine()

class Dummy_grep:
    grep_it = GrepDialog.grep_it.im_func
    findfiles = GrepDialog.findfiles.im_func
    recvar = Var(False)
    engine = searchengine

    def close(self):
        pass


grep = Dummy_grep()

class FindfilesTest(unittest.TestCase):
    pass


class Grep_itTest(unittest.TestCase):

    def report(self, pat):
        grep.engine._pat = pat
        with captured_stdout() as s:
            grep.grep_it(re.compile(pat), __file__)
        lines = s.getvalue().split('\n')
        lines.pop()
        return lines

    def test_unfound(self):
        pat = 'xyz*' * 7
        lines = self.report(pat)
        self.assertEqual(len(lines), 2)
        self.assertIn(pat, lines[0])
        self.assertEqual(lines[1], 'No hits.')

    def test_found(self):
        pat = '""" !Changing this line will break Test_findfile.test_found!'
        lines = self.report(pat)
        self.assertEqual(len(lines), 5)
        self.assertIn(pat, lines[0])
        self.assertIn('py: 1:', lines[1])
        self.assertIn('2', lines[3])
        self.assertTrue(lines[4].startswith('(Hint:'))


class Default_commandTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
