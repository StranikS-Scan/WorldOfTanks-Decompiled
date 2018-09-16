# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle_test/htest.py
from importlib import import_module
import Tkinter as tk
_Editor_window_spec = {'file': 'EditorWindow',
 'kwds': {},
 'msg': 'Test editor functions of interest'}
_Help_dialog_spec = {'file': 'EditorWindow',
 'kwds': {},
 'msg': 'If the help text displays, this works'}
AboutDialog_spec = {'file': 'aboutDialog',
 'kwds': {'title': 'About test'},
 'msg': 'Try each button'}
GetCfgSectionNameDialog_spec = {'file': 'configSectionNameDialog',
 'kwds': {'title': 'Get Name',
          'message': 'Enter something',
          'used_names': {'abc'},
          '_htest': True},
 'msg': "After the text entered with [Ok] is stripped, <nothing>, 'abc', or more that 30 chars are errors.\nClose 'Get Name' with a valid entry (printed to Shell), [Cancel], or [X]"}

def run(test):
    root = tk.Tk()
    test_spec = globals()[test.__name__ + '_spec']
    test_kwds = test_spec['kwds']
    test_kwds['parent'] = root

    def run_test():
        widget = test(**test_kwds)
        try:
            print widget.result
        except AttributeError:
            pass

    tk.Label(root, text=test_spec['msg'], justify='left').pack()
    tk.Button(root, text='Test ' + test.__name__, command=run_test).pack()
    root.mainloop()


def runall():
    for k, d in globals().items():
        if k.endswith('_spec'):
            mod = import_module('idlelib.' + d['file'])
            test = getattr(mod, k[:-5])
            run(test)


if __name__ == '__main__':
    runall()
