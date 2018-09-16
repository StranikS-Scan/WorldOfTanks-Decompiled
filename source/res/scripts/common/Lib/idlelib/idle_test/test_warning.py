# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/test_warning.py
import unittest
from test.test_support import captured_stderr
import warnings
showwarning = warnings.showwarning
running_in_idle = 'idle' in showwarning.__name__
from idlelib import run
from idlelib import PyShell as shell
idlemsg = '\nWarning (from warnings module):\n  File "test_warning.py", line 99\n    Line of code\nUserWarning: Test\n'
shellmsg = idlemsg + '>>> '

class RunWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_idle, 'Does not work when run within Idle.')
    def test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        run.capture_warnings(True)
        self.assertIs(warnings.showwarning, run.idle_showwarning_subproc)
        run.capture_warnings(False)
        self.assertIs(warnings.showwarning, showwarning)

    def test_run_show(self):
        with captured_stderr() as f:
            run.idle_showwarning_subproc('Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            self.assertEqual(idlemsg.splitlines(), f.getvalue().splitlines())


class ShellWarnTest(unittest.TestCase):

    @unittest.skipIf(running_in_idle, 'Does not work when run within Idle.')
    def test_showwarnings(self):
        self.assertIs(warnings.showwarning, showwarning)
        shell.capture_warnings(True)
        self.assertIs(warnings.showwarning, shell.idle_showwarning)
        shell.capture_warnings(False)
        self.assertIs(warnings.showwarning, showwarning)

    def test_idle_formatter(self):
        s = shell.idle_formatwarning('Test', UserWarning, 'test_warning.py', 99, 'Line of code')
        self.assertEqual(idlemsg, s)

    def test_shell_show(self):
        with captured_stderr() as f:
            shell.idle_showwarning('Test', UserWarning, 'test_warning.py', 99, f, 'Line of code')
            self.assertEqual(shellmsg.splitlines(), f.getvalue().splitlines())


if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
