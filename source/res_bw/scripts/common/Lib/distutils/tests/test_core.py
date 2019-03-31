# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_core.py
# Compiled at: 2010-10-21 18:49:01
"""Tests for distutils.core."""
import StringIO
import distutils.core
import os
import shutil
import sys
import test.test_support
import unittest
setup_using___file__ = '\n__file__\n\nfrom distutils.core import setup\nsetup()\n'
setup_prints_cwd = '\nimport os\nprint os.getcwd()\n\nfrom distutils.core import setup\nsetup()\n'

class CoreTestCase(unittest.TestCase):

    def setUp(self):
        self.old_stdout = sys.stdout
        self.cleanup_testfn()

    def tearDown(self):
        sys.stdout = self.old_stdout
        self.cleanup_testfn()

    def cleanup_testfn(self):
        path = test.test_support.TESTFN
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def write_setup(self, text, path=test.test_support.TESTFN):
        open(path, 'w').write(text)
        return path

    def test_run_setup_provides_file(self):
        distutils.core.run_setup(self.write_setup(setup_using___file__))

    def test_run_setup_uses_current_dir(self):
        sys.stdout = StringIO.StringIO()
        cwd = os.getcwd()
        os.mkdir(test.test_support.TESTFN)
        setup_py = os.path.join(test.test_support.TESTFN, 'setup.py')
        distutils.core.run_setup(self.write_setup(setup_prints_cwd, path=setup_py))
        output = sys.stdout.getvalue()
        if output.endswith('\n'):
            output = output[:-1]
        self.assertEqual(cwd, output)


def test_suite():
    return unittest.makeSuite(CoreTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
