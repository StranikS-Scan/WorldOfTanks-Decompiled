# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/distutils/tests/test_core.py
import StringIO
import distutils.core
import os
import shutil
import sys
import test.test_support
from test.test_support import captured_stdout, run_unittest
import unittest
from distutils.tests import support
from distutils import log
setup_using___file__ = '\n__file__\n\nfrom distutils.core import setup\nsetup()\n'
setup_prints_cwd = '\nimport os\nprint os.getcwd()\n\nfrom distutils.core import setup\nsetup()\n'

class CoreTestCase(support.EnvironGuard, unittest.TestCase):

    def setUp(self):
        super(CoreTestCase, self).setUp()
        self.old_stdout = sys.stdout
        self.cleanup_testfn()
        self.old_argv = (sys.argv, sys.argv[:])
        self.addCleanup(log.set_threshold, log._global_log.threshold)

    def tearDown(self):
        sys.stdout = self.old_stdout
        self.cleanup_testfn()
        sys.argv = self.old_argv[0]
        sys.argv[:] = self.old_argv[1]
        super(CoreTestCase, self).tearDown()

    def cleanup_testfn(self):
        path = test.test_support.TESTFN
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def write_setup(self, text, path=test.test_support.TESTFN):
        f = open(path, 'w')
        try:
            f.write(text)
        finally:
            f.close()

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

    def test_debug_mode(self):
        sys.argv = ['setup.py', '--name']
        with captured_stdout() as stdout:
            distutils.core.setup(name='bar')
        stdout.seek(0)
        self.assertEqual(stdout.read(), 'bar\n')
        distutils.core.DEBUG = True
        try:
            with captured_stdout() as stdout:
                distutils.core.setup(name='bar')
        finally:
            distutils.core.DEBUG = False

        stdout.seek(0)
        wanted = 'options (after parsing config files):\n'
        self.assertEqual(stdout.readlines()[0], wanted)


def test_suite():
    return unittest.makeSuite(CoreTestCase)


if __name__ == '__main__':
    run_unittest(test_suite())
