# Embedded file name: scripts/common/Lib/lib-tk/test/test_tkinter/test_loadtk.py
import os
import sys
import unittest
from test import test_support
from Tkinter import Tcl, TclError
test_support.requires('gui')

class TkLoadTest(unittest.TestCase):

    @unittest.skipIf('DISPLAY' not in os.environ, 'No $DISPLAY set.')
    def testLoadTk(self):
        tcl = Tcl()
        self.assertRaises(TclError, tcl.winfo_geometry)
        tcl.loadtk()
        self.assertEqual('1x1+0+0', tcl.winfo_geometry())
        tcl.destroy()

    def testLoadTkFailure(self):
        old_display = None
        if sys.platform.startswith(('win', 'darwin', 'cygwin')):
            return
        else:
            with test_support.EnvironmentVarGuard() as env:
                if 'DISPLAY' in os.environ:
                    del env['DISPLAY']
                    display = os.popen('echo $DISPLAY').read().strip()
                    if display:
                        return
                tcl = Tcl()
                self.assertRaises(TclError, tcl.winfo_geometry)
                self.assertRaises(TclError, tcl.loadtk)
            return


tests_gui = (TkLoadTest,)
if __name__ == '__main__':
    test_support.run_unittest(*tests_gui)
