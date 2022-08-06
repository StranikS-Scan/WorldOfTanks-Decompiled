# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/test_pathbrowser.py
import unittest
import os
import sys
import idlelib
from idlelib import PathBrowser

class PathBrowserTest(unittest.TestCase):

    def test_DirBrowserTreeItem(self):
        d = PathBrowser.DirBrowserTreeItem('')
        d.GetSubList()
        self.assertEqual('', d.GetText())
        dir = os.path.split(os.path.abspath(idlelib.__file__))[0]
        self.assertEqual(d.ispackagedir(dir), True)
        self.assertEqual(d.ispackagedir(dir + '/Icons'), False)

    def test_PathBrowserTreeItem(self):
        p = PathBrowser.PathBrowserTreeItem()
        self.assertEqual(p.GetText(), 'sys.path')
        sub = p.GetSubList()
        self.assertEqual(len(sub), len(sys.path))


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
