# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/WidgetRedirector.py
from Tkinter import *

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
        del self.widget
        orig = self.orig
        del self.orig
        tk = widget.tk
        w = widget._w
        tk.deletecommand(w)
        tk.call('rename', orig, w)

    def register(self, operation, function):
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        return OriginalCommand(self, operation)

    def unregister(self, operation):
        if operation in self._operations:
            function = self._operations[operation]
            del self._operations[operation]
            if hasattr(self.widget, operation):
                delattr(self.widget, operation)
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
        self.tk_call = self.tk.call
        self.orig_and_operation = (self.orig, self.operation)

    def __repr__(self):
        return 'OriginalCommand(%r, %r)' % (self.redir, self.operation)

    def __call__(self, *args):
        return self.tk_call(self.orig_and_operation + args)


def main():
    global previous_tcl_fcn
    root = Tk()
    root.wm_protocol('WM_DELETE_WINDOW', root.quit)
    text = Text()
    text.pack()
    text.focus_set()
    redir = WidgetRedirector(text)

    def my_insert(*args):
        print 'insert', args
        previous_tcl_fcn(*args)

    previous_tcl_fcn = redir.register('insert', my_insert)
    root.mainloop()
    redir.unregister('insert')
    redir.close()
    root.mainloop()
    root.destroy()


if __name__ == '__main__':
    main()
