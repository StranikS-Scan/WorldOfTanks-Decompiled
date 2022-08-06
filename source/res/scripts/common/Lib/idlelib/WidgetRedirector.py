# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/WidgetRedirector.py
from __future__ import print_function
from Tkinter import TclError

class WidgetRedirector:

    def __init__(self, widget):
        self._operations = {}
        self.widget = widget
        self.tk = tk = widget.tk
        w = widget._w
        self.orig = w + '_orig'
        tk.call('rename', w, self.orig)
        tk.createcommand(w, self.dispatch)

    def __repr__(self):
        return 'WidgetRedirector(%s<%s>)' % (self.widget.__class__.__name__, self.widget._w)

    def close(self):
        for operation in list(self._operations):
            self.unregister(operation)

        widget = self.widget
        tk = widget.tk
        w = widget._w
        tk.deletecommand(w)
        tk.call('rename', self.orig, w)
        del self.widget
        del self.tk

    def register(self, operation, function):
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        return OriginalCommand(self, operation)

    def unregister(self, operation):
        if operation in self._operations:
            function = self._operations[operation]
            del self._operations[operation]
            try:
                delattr(self.widget, operation)
            except AttributeError:
                pass

            return function
        else:
            return None
            return None

    def dispatch(self, operation, *args):
        m = self._operations.get(operation)
        try:
            if m:
                return m(*args)
            return self.tk.call((self.orig, operation) + args)
        except TclError:
            return ''


class OriginalCommand:

    def __init__(self, redir, operation):
        self.redir = redir
        self.operation = operation
        self.tk = redir.tk
        self.orig = redir.orig
        self.tk_call = redir.tk.call
        self.orig_and_operation = (redir.orig, operation)

    def __repr__(self):
        return 'OriginalCommand(%r, %r)' % (self.redir, self.operation)

    def __call__(self, *args):
        return self.tk_call(self.orig_and_operation + args)


def _widget_redirector(parent):
    from Tkinter import Tk, Text
    import re
    root = Tk()
    root.title('Test WidgetRedirector')
    width, height, x, y = list(map(int, re.split('[x+]', parent.geometry())))
    root.geometry('+%d+%d' % (x, y + 150))
    text = Text(root)
    text.pack()
    text.focus_set()
    redir = WidgetRedirector(text)

    def my_insert(*args):
        print('insert', args)
        original_insert(*args)

    original_insert = redir.register('insert', my_insert)
    root.mainloop()


if __name__ == '__main__':
    import unittest
    unittest.main('idlelib.idle_test.test_widgetredir', verbosity=2, exit=False)
    from idlelib.idle_test.htest import run
    run(_widget_redirector)
